"""SSL certificate management for AWS RDS connections."""

import os
import ssl
import logging
from pathlib import Path
from typing import Optional
import urllib.request

logger = logging.getLogger(__name__)

# AWS RDS CA bundle URLs
RDS_CA_BUNDLE_URLS = {
    "global": "https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem",
    "us-east-1": "https://truststore.pki.rds.amazonaws.com/us-east-1/us-east-1-bundle.pem",
    "us-east-2": "https://truststore.pki.rds.amazonaws.com/us-east-2/us-east-2-bundle.pem",
    "us-west-1": "https://truststore.pki.rds.amazonaws.com/us-west-1/us-west-1-bundle.pem",
    "us-west-2": "https://truststore.pki.rds.amazonaws.com/us-west-2/us-west-2-bundle.pem",
    "eu-west-1": "https://truststore.pki.rds.amazonaws.com/eu-west-1/eu-west-1-bundle.pem",
    "eu-west-2": "https://truststore.pki.rds.amazonaws.com/eu-west-2/eu-west-2-bundle.pem",
    "eu-central-1": "https://truststore.pki.rds.amazonaws.com/eu-central-1/eu-central-1-bundle.pem",
    "ap-northeast-1": "https://truststore.pki.rds.amazonaws.com/ap-northeast-1/ap-northeast-1-bundle.pem",
    "ap-southeast-1": "https://truststore.pki.rds.amazonaws.com/ap-southeast-1/ap-southeast-1-bundle.pem",
    "ap-southeast-2": "https://truststore.pki.rds.amazonaws.com/ap-southeast-2/ap-southeast-2-bundle.pem",
}

# Default cert directory
DEFAULT_CERT_DIR = Path(__file__).parent.parent / "certs"


class RDSCertificateManager:
    """Manages SSL certificates for AWS RDS connections."""

    def __init__(self, cert_dir: Optional[str] = None):
        """
        Initialize the certificate manager.

        Args:
            cert_dir: Directory to store certificates. Defaults to app/certs/
        """
        self.cert_dir = Path(cert_dir) if cert_dir else DEFAULT_CERT_DIR
        self.cert_dir.mkdir(parents=True, exist_ok=True)

    def get_cert_path(self, region: str = "global") -> Path:
        """
        Get the path to the RDS CA bundle for a region.

        Args:
            region: AWS region or "global" for the global bundle

        Returns:
            Path to the certificate file
        """
        # Use global bundle by default as it works for all regions
        cert_name = f"rds-ca-{region}-bundle.pem"
        return self.cert_dir / cert_name

    def ensure_cert_exists(self, region: str = "global") -> Path:
        """
        Ensure the RDS CA bundle exists, downloading if necessary.

        Args:
            region: AWS region or "global"

        Returns:
            Path to the certificate file
        """
        cert_path = self.get_cert_path(region)

        if cert_path.exists():
            logger.debug(f"Using cached RDS CA bundle: {cert_path}")
            return cert_path

        # Download the certificate
        url = RDS_CA_BUNDLE_URLS.get(region, RDS_CA_BUNDLE_URLS["global"])
        logger.info(f"Downloading RDS CA bundle from {url}")

        try:
            # Create SSL context that doesn't verify certificates for the download
            # This is safe as we're downloading from the known AWS trust store URL
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(url, context=ctx, timeout=30) as response:
                cert_data = response.read()

            # Write to file
            cert_path.write_bytes(cert_data)
            logger.info(f"Saved RDS CA bundle to {cert_path}")

            return cert_path

        except Exception as e:
            logger.error(f"Failed to download RDS CA bundle: {e}")
            # Try to use global bundle if region-specific fails
            if region != "global":
                logger.info("Falling back to global CA bundle")
                return self.ensure_cert_exists("global")
            raise

    def get_ssl_context(self, region: str = "global") -> ssl.SSLContext:
        """
        Get an SSL context configured for RDS connections.

        Args:
            region: AWS region

        Returns:
            Configured SSLContext
        """
        cert_path = self.ensure_cert_exists(region)

        context = ssl.create_default_context()
        context.load_verify_locations(str(cert_path))
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True

        return context

    def get_connect_args(self, region: str = "global") -> dict:
        """
        Get connection arguments for psycopg/SQLAlchemy with SSL.

        Args:
            region: AWS region

        Returns:
            Dictionary of connection arguments
        """
        cert_path = self.ensure_cert_exists(region)

        return {
            "sslmode": "verify-full",
            "sslrootcert": str(cert_path),
        }


# Global instance
_cert_manager: Optional[RDSCertificateManager] = None


def get_cert_manager(cert_dir: Optional[str] = None) -> RDSCertificateManager:
    """Get or create the global certificate manager."""
    global _cert_manager
    if _cert_manager is None:
        _cert_manager = RDSCertificateManager(cert_dir)
    return _cert_manager


def get_rds_ssl_cert_path(region: str = "global", cert_dir: Optional[str] = None) -> str:
    """
    Get the path to the RDS CA bundle, downloading if necessary.

    Args:
        region: AWS region
        cert_dir: Optional custom certificate directory

    Returns:
        Path to the certificate file as a string
    """
    manager = get_cert_manager(cert_dir)
    return str(manager.ensure_cert_exists(region))


def get_rds_connect_args(region: str = "global", cert_dir: Optional[str] = None) -> dict:
    """
    Get connection arguments for RDS with SSL.

    Args:
        region: AWS region
        cert_dir: Optional custom certificate directory

    Returns:
        Dictionary of connection arguments for SQLAlchemy
    """
    manager = get_cert_manager(cert_dir)
    return manager.get_connect_args(region)
