from pytz import utc
from jwt import decode
from jwt.exceptions import InvalidTokenError
from datetime import datetime
from urllib.parse import urlparse
from typing import Union, Dict, Optional

from stellar_sdk import Keypair
from stellar_sdk.exceptions import Ed25519PublicKeyInvalidError

from polaris import settings


print("Usando core.testing.sep10.token")
class SEP10Token:
    _REQUIRED_FIELDS = {"iss", "sub", "iat", "exp"}

    def __init__(self, jwt: Union[str, Dict]):
        if isinstance(jwt, str):
            try:
                jwt = decode(jwt, settings.SERVER_JWT_KEY, algorithms=["HS256"])
            except InvalidTokenError:
                raise ValueError("unable to decode jwt")
        elif not isinstance(jwt, Dict):
            raise ValueError(
                "invalid type for 'jwt' parameter: must be a string or dictionary"
            )

        if not self._REQUIRED_FIELDS.issubset(set(jwt.keys())):
            raise ValueError(
                f"jwt is missing one of the required fields: {', '.join(self._REQUIRED_FIELDS)}"
            )

        try:
            Keypair.from_public_key(jwt["sub"])
        except Ed25519PublicKeyInvalidError:
            raise ValueError(f"invalid Stellar public key: {jwt['sub']}")

        try:
            iat = datetime.fromtimestamp(jwt["iat"], tz=utc)
        except (OSError, ValueError, OverflowError):
            raise ValueError("invalid iat value")
        try:
            exp = datetime.fromtimestamp(jwt["exp"], tz=utc)
        except (OSError, ValueError, OverflowError):
            raise ValueError("invalid exp value")

        now = datetime.now(tz=utc)
        if now < iat or now > exp:
            raise ValueError("jwt is no longer valid")

        client_domain = jwt.get("client_domain")
        if (
            client_domain
            and urlparse(f"https://{client_domain}").netloc != client_domain
        ):
            raise ValueError("'client_domain' must be a hostname")

        self._payload = jwt

    @property
    def account(self) -> str:
        return self._payload["sub"]

    @property
    def issuer(self) -> str:
        return self._payload["iss"]

    @property
    def issued_at(self) -> datetime:
        return datetime.fromtimestamp(self._payload["iat"], tz=utc)

    @property
    def expires_at(self) -> datetime:
        return datetime.fromtimestamp(self._payload["exp"], tz=utc)

    @property
    def client_domain(self) -> Optional[str]:
        return self._payload.get("client_domain")

    @property
    def payload(self) -> dict:
        return self._payload
