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
        python = pkgs.python312;
      in
      {
        packages.default = python.pkgs.buildPythonPackage {
          pname = "cloud-pyprland";
          version = "0.1.0";
          pyproject = true;
          src = ./.;

          nativeBuildInputs = with python.pkgs; [ poetry-core ];
          propagatedBuildInputs = with python.pkgs; [
            pyprland
            requests
          ];

          pythonImportsCheck = [ "cloud_pyprland" ];
        };

        devShells.default = pkgs.mkShell {
          packages = [
            python
            pkgs.poetry
          ];
        };
      });
}
