"""Google Workspace connection foundation with no domain-data access."""

from src.connectors.google_workspace.credential_vault import (
    EncryptedGoogleCredentialVault,
    GoogleCredentialVaultError,
    WindowsDpapiProtector,
)
from src.connectors.google_workspace.manager import (
    GoogleReconnectRequired,
    GoogleWorkspaceConnectionManager,
    GoogleWorkspaceFoundationError,
)
from src.connectors.google_workspace.models import (
    FOUNDATION_PROFILE_ID,
    FOUNDATION_SCOPES,
    GoogleConnectionState,
    GoogleConnectionStatus,
    GoogleGrantProfile,
    GoogleGrantProfileCatalog,
    GoogleScopeInventory,
    GoogleWorkspaceAccount,
    mask_google_account,
)
from src.connectors.google_workspace.oauth import (
    GoogleAuthorizationRequest,
    GoogleLoopbackCallbackReceiver,
    GoogleOAuthClientConfig,
    GoogleOAuthError,
    GoogleOAuthNetworkTransport,
    GoogleOAuthProtocolError,
)

__all__ = [
    "EncryptedGoogleCredentialVault",
    "FOUNDATION_PROFILE_ID",
    "FOUNDATION_SCOPES",
    "GoogleAuthorizationRequest",
    "GoogleConnectionState",
    "GoogleConnectionStatus",
    "GoogleCredentialVaultError",
    "GoogleGrantProfile",
    "GoogleGrantProfileCatalog",
    "GoogleLoopbackCallbackReceiver",
    "GoogleOAuthClientConfig",
    "GoogleOAuthError",
    "GoogleOAuthNetworkTransport",
    "GoogleOAuthProtocolError",
    "GoogleReconnectRequired",
    "GoogleScopeInventory",
    "GoogleWorkspaceAccount",
    "GoogleWorkspaceConnectionManager",
    "GoogleWorkspaceFoundationError",
    "WindowsDpapiProtector",
    "mask_google_account",
]
