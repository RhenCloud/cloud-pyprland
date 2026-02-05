{
  description = "Nix packaging for cloud-pyprland";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        pythonPkg = pkgs.python3Packages.buildPythonPackage rec {
          pname = "cloud-pyprland";
          version = "0.1.0";
          pyproject = true;
          # 自动读取 pyproject.toml/源代码
          src = ./.;

          nativeBuildInputs = [
            pkgs.python3Packages.poetry-core
          ];

          propagatedBuildInputs = with pkgs; [
            python3Packages.requests
            # pyprland
          ];

          meta = with pkgs.lib; {
            description = "RhenCloud's plugins for pyprland";
            license = licenses.mit;
            maintainers = [ maintainers.something ];
          };
        };
      in
      {
        packages.default = pythonPkg;
      });
}


