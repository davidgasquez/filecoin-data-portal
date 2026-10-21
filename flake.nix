{
  description = "Filecoin Data Portal development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    llm-agents.url = "github:numtide/llm-agents.nix";
  };

  outputs =
    { nixpkgs, llm-agents, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = [
            pkgs.uv
            pkgs.python314
            pkgs.nodejs_22
            pkgs.gnumake
            # Keep on the same minor version as the Python duckdb package in uv.lock.
            pkgs.duckdb
            llm-agents.packages.${pkgs.stdenv.hostPlatform.system}.qmd
          ];

          # Use Nix's Python instead of downloading a generic interpreter.
          UV_PYTHON = "${pkgs.python314}/bin/python3.14";
          UV_PYTHON_DOWNLOADS = "never";

          # Binary Python wheels (DuckDB, PyArrow, etc.) need the C++ runtime.
          shellHook = ''
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib ]}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
          '';
        };
      });
    };
}
