set -e

A=$(mktemp)

cat $1 | perl -e 'use Compress::Raw::Zlib;my $d=new Compress::Raw::Zlib::Inflate();my $o;undef $/;$d->inflate(<>,$o);print $o;' > $A && mv $A $1
