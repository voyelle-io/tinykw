#!/bin/bash
set -e

VERSION_TAG=$1

for plat_dir in libs/*/; do
    plat_dir="${plat_dir%/}" 
    plat_name="${plat_dir##*/}"
    DEPLOY_DIR="deploy_$plat_name"

    # copy header
    mkdir -p "$DEPLOY_DIR/include"
    cp "$plat_dir/tinykw.h" "$DEPLOY_DIR/include/"

    # copy lib
    mkdir -p "$DEPLOY_DIR/lib"
    for lang_dir in ${plat_dir}/*/; do
        lang_dir="${lang_dir%/}" 
        cp -r "$lang_dir" "$DEPLOY_DIR/lib/"
    done

    # copy license
    cp LICENSE "$DEPLOY_DIR/"

    cd $DEPLOY_DIR
    zip -r "../tinykw-${plat_name}-${VERSION_TAG}.zip" . -x "*.DS_Store"
    cd ..

    rm -rf "$DEPLOY_DIR"
done
