bundle DURATION="":
    ./scripts/create-bundle.sh {{DURATION}}

buildpkgs TAG="":
    ./scripts/build-pkgs.sh {{TAG}}

test:
    ./scripts/pytest.sh