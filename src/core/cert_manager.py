import ipaddress
import os
import ssl
import logging
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

logger = logging.getLogger('Pretender.Cert')


class CertManager:
    """CA 证书管理 + 域名证书动态签发/缓存"""

    def __init__(self, certs_dir='certs'):
        self.certs_dir = certs_dir
        self.domains_dir = os.path.join(certs_dir, 'domains')
        self._domain_cache = {}  # domain -> (cert_path, key_path)
        self._ca_key = None
        self._ca_cert = None
        self._ensure_ca()

    # ── CA 管理 ──────────────────────────────────────────

    def _ensure_ca(self):
        """确保 CA 证书存在，不存在则生成"""
        os.makedirs(self.domains_dir, exist_ok=True)

        ca_key_path = os.path.join(self.certs_dir, 'ca.key')
        ca_crt_path = os.path.join(self.certs_dir, 'ca.crt')

        if os.path.exists(ca_key_path) and os.path.exists(ca_crt_path):
            # 加载已有 CA
            with open(ca_key_path, 'rb') as f:
                self._ca_key = serialization.load_pem_private_key(f.read(), password=None)
            with open(ca_crt_path, 'rb') as f:
                self._ca_cert = x509.load_pem_x509_certificate(f.read())
            logger.info(f"CA 证书已加载: {ca_crt_path}")
        else:
            self._generate_ca(ca_key_path, ca_crt_path)

    def _generate_ca(self, key_path, crt_path):
        """生成自签名 Root CA（2048-bit RSA，有效期 10 年）"""
        self._ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, 'CN'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Pretender Proxy'),
            x509.NameAttribute(NameOID.COMMON_NAME, 'Pretender Root CA'),
        ])

        self._ca_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self._ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True, key_cert_sign=True, crl_sign=True,
                    content_commitment=False, key_encipherment=False,
                    data_encipherment=False, key_agreement=False,
                    encipher_only=False, decipher_only=False,
                ),
                critical=True,
            )
            .sign(self._ca_key, hashes.SHA256())
        )

        with open(key_path, 'wb') as f:
            f.write(self._ca_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ))

        with open(crt_path, 'wb') as f:
            f.write(self._ca_cert.public_bytes(serialization.Encoding.PEM))

        logger.info(f"CA 证书已生成: {crt_path}")

    # ── 域名证书签发 ──────────────────────────────────────

    def get_cert_for_domain(self, domain):
        """获取域名证书路径，内存缓存 → 磁盘缓存 → 动态生成"""
        if domain in self._domain_cache:
            return self._domain_cache[domain]

        cert_path = os.path.join(self.domains_dir, f'{domain}.crt')
        key_path = os.path.join(self.domains_dir, f'{domain}.key')

        if os.path.exists(cert_path) and os.path.exists(key_path):
            self._domain_cache[domain] = (cert_path, key_path)
            return cert_path, key_path

        # 动态生成
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, domain),
        ])

        # IP 地址用 IPAddress SAN，域名用 DNSName SAN
        try:
            ip = ipaddress.ip_address(domain)
            san = x509.SubjectAlternativeName([x509.IPAddress(ip)])
        except ValueError:
            san = x509.SubjectAlternativeName([x509.DNSName(domain)])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self._ca_cert.subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .add_extension(san, critical=False)
            .sign(self._ca_key, hashes.SHA256())
        )

        with open(key_path, 'wb') as f:
            f.write(key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ))

        with open(cert_path, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        logger.info(f"域名证书已生成: {domain}")
        self._domain_cache[domain] = (cert_path, key_path)
        return cert_path, key_path

    def get_ssl_context(self, domain):
        """为域名创建 server-side SSLContext"""
        cert_path, key_path = self.get_cert_for_domain(domain)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert_path, key_path)
        return ctx
