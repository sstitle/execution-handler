{
  description = "Development environment with nickel and mask";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-parts.url = "github:hercules-ci/flake-parts";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    inputs@{ self, flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];

      perSystem =
        {
          config,
          self',
          inputs',
          pkgs,
          system,
          ...
        }:
        let
          treefmtEval = inputs.treefmt-nix.lib.evalModule pkgs ./treefmt.nix;
        in
        {
          packages = {
            default = pkgs.stdenv.mkDerivation {
              pname = "execution-handler";
              version = "0.1.0";

              src = ./.;
              name = "execution-handler-${
                pkgs.lib.substring 0 8 (builtins.hashString "sha256" (builtins.readFile ./pyproject.toml))
              }";

              buildInputs = with pkgs; [
                uv
                python3
              ];

              # Enable testing during build
              doCheck = true;

              buildPhase = ''
                # Set up uv environment for Nix build
                export UV_CACHE_DIR=$TMPDIR/uv-cache
                export UV_DATA_DIR=$TMPDIR/uv-data
                export UV_COMPILE_BYTECODE=1
                export UV_LINK_MODE=copy
                export UV_NO_SYNC=1
                export HOME=$TMPDIR/home

                # Create directories for uv data
                mkdir -p $UV_CACHE_DIR
                mkdir -p $UV_DATA_DIR
                mkdir -p $HOME/.local/share/uv

                # Install dependencies directly without creating a venv
                uv pip install --system --target $out/lib/python3.13/site-packages -r <(uv export --format requirements-txt --no-hashes)
              '';

              checkPhase = ''
                # Set up environment for tests
                export PYTHONPATH=$out/lib/python3.13/site-packages:$PWD:$PYTHONPATH
                export UV_CACHE_DIR=$TMPDIR/uv-cache
                export UV_DATA_DIR=$TMPDIR/uv-data
                export HOME=$TMPDIR/home

                # Run tests with pytest
                ${pkgs.python3}/bin/python -m pytest tests/ -v --tb=short
              '';

              installPhase = ''
                mkdir -p $out/bin

                # Copy the entire project structure
                cp -r . $out/

                # Create a wrapper script that runs the main Python script
                cat > $out/bin/execution-handler << EOF
                #!${pkgs.bash}/bin/bash
                cd $out
                export PYTHONPATH=$out/lib/python3.13/site-packages:\$PYTHONPATH
                exec ${pkgs.python3}/bin/python execution_handler.py "\$@"
                EOF
                chmod +x $out/bin/execution-handler

                # Also provide direct access to the Python module
                cat > $out/bin/execution-handler-main << EOF
                #!${pkgs.bash}/bin/bash
                cd $out
                export PYTHONPATH=$out/lib/python3.13/site-packages:\$PYTHONPATH
                exec ${pkgs.python3}/bin/python -m src "\$@"
                EOF
                chmod +x $out/bin/execution-handler-main
              '';
            };
          };

          # Make the package runnable with `nix run`
          apps.default = {
            type = "app";
            program = "${self.packages.${system}.default}/bin/execution-handler";
          };

          # Development shell with nickel and mask
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              # Core tools
              git
              mask

              # python
              uv
            ];

            shellHook = ''
              echo "🚀 Development environment loaded!"
              echo "Available tools:"
              echo "  - nickel: Configuration language"
              echo "  - mask: Task runner"
              echo ""
              echo "Run 'mask --help' to see available tasks."
              echo "Run 'nix fmt' to format all files."
            '';
          };

          # for `nix fmt`
          formatter = treefmtEval.config.build.wrapper;

          # for `nix flake check`
          checks = {
            formatting = treefmtEval.config.build.check self;
          };
        };
    };
}
