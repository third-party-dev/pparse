#!/usr/bin/env bash

export PROJ_PATH=$(realpath $(dirname $0)/..)
cd ${PROJ_PATH}

# Note: VERSION is git-ignored (not revision controlled)
if [ -z "$1" ]; then
  VERSION="0.0.0.dev0"
else
  VERSION=$1
fi

echo "$VERSION" > ${PROJ_PATH}/VERSION

python -m build --no-isolation --outdir ${PROJ_PATH}/outputs/dist
python -m build --no-isolation --sdist --outdir ${PROJ_PATH}/outputs/dist

# Build a minimal set of packages for offline deployments.
pushd outputs/dist
PIP_PKG_PATH=pparse-pip-pkgs-py$(python --version | awk '{print $2}')-$VERSION
mkdir -p $PIP_PKG_PATH
#echo "pip download -f . -d $PIP_PKG_PATH \"thirdparty-pparse==$VERSION\""
pip download -f . -d $PIP_PKG_PATH "thirdparty-pparse==$VERSION"
echo "thirdparty-pparse==$VERSION" > $PIP_PKG_PATH/requirements.txt
tar -czf $PIP_PKG_PATH.tar.gz $PIP_PKG_PATH
popd

echo "!! Ensure clean repo before tagging. !!"
echo
echo git tag v$VERSION
echo
echo git push origin v$VERSION
echo