# nix/packages.nix — Private Agent package built with uv2nix
{ inputs, ... }:
{
  perSystem =
    { pkgs, lib, inputs', ... }:
    let
      PrivateAgent = pkgs.callPackage ./Private-agent.nix {
        inherit (inputs) uv2nix pyproject-nix pyproject-build-systems;
        npm-lockfile-fix = inputs'.npm-lockfile-fix.packages.default;
        # Only embed clean revs — dirtyRev doesn't represent any upstream
        # commit, so comparing it would always claim "update available".
        rev = inputs.self.rev or null;
      };
    in
    {
      packages = {
        default = PrivateAgent;

        # Ships discord.py + python-telegram-bot + slack-sdk so a plain
        # `nix profile install .#messaging` connects to Discord/Telegram/Slack
        # on first run — lazy-install can't write to the read-only /nix/store.
        messaging = PrivateAgent.override {
          extraDependencyGroups = [ "messaging" ];
        };

        # All platform-portable optional integrations pre-built.
        # matrix is Linux-only (oqs/liboqs lacks aarch64-darwin wheels).
        full = PrivateAgent.override {
          extraDependencyGroups = [
            "anthropic"
            "azure-identity"
            "bedrock"
            "daytona"
            "dingtalk"
            "edge-tts"
            "exa"
            "fal"
            "feishu"
            "firecrawl"
            "hindsight"
            "honcho"
            "messaging"
            "modal"
            "parallel-web"
            "tts-premium"
            "voice"
          ] ++ lib.optionals pkgs.stdenv.isLinux [ "matrix" ];
        };

        tui = PrivateAgent.PrivateTui;
        web = PrivateAgent.PrivateWeb;
        desktop = PrivateAgent.PrivateDesktop;

        fix-lockfiles = PrivateAgent.PrivateNpmLib.mkFixLockfiles { attr = "tui"; };
      };
    };
}
