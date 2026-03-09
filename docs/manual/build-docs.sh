#!/usr/bin/env bash

# sudo apt-get update
# sudo apt-get install pandoc
# sudo apt install texlive-xetex texlive-latex-extra librsvg2-bin
# sudo apt install texlive-fonts-extra

# adjustbox babel-german background bidi collectbox csquotes everypage filehook
# footmisc footnotebackref framed fvextra letltxmacro ly1 mdframed mweights
# needspace pagecolor sourcecodepro sourcesanspro titling ucharcat
# unicode-math upquote xecjk xurl zref draftwatermark

# tlmgr install soul adjustbox babel-german background bidi collectbox csquotes everypage filehook footmisc footnotebackref framed fvextra letltxmacro ly1 mdframed mweights needspace pagecolor sourcecodepro sourcesanspro titling ucharcat unicode-math upquote xecjk xurl zref draftwatermark

# Optionally Install From Upstream
# wget https://github.com/jgm/pandoc/releases/download/<version>/pandoc-<version>-1-amd64.deb
# sudo dpkg -i pandoc-<version>-1-amd64.deb
# sudo apt -f install   # to fix any missing dependencies

# pandoc *.md --toc --number-sections --pdf-engine=xelatex -o book.pdf

CHAPTERS="
0-docs.md
"

# --number-sections
# --listings

# NOTE: Ensure images have sufficiently high DPI. A standard 96 DPI image from a screenshot
#       will be oversized in the PDF. Try something like 300DPI or higher. FYI, most home
#       inkjet printers are 300-600 DPI, so this lines up. You can scale image DPI up and
#       down all day long and it will create zero pixel loss. Only the DPI header value
#       changes.

echo "Building JSON."
pandoc metadata.yaml $CHAPTERS metadata-tail.yaml -t json > book.json

echo "Building PDF."
pandoc metadata.yaml $CHAPTERS metadata-tail.yaml \
  --toc --pdf-engine=xelatex --template=template/eisvogel.tex \
  --lua-filter=pandoc-filter.lua -o book.pdf #--verbose

echo "Building EPUB."
pandoc metadata.yaml $CHAPTERS metadata-tail.yaml --toc -o book.epub

