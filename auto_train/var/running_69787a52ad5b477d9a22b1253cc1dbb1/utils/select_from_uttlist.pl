#!/usr/bin/perl -W
# License: GPL-2

use strict;
use warnings;

 if (@ARGV < 3)
 {
     print "usage:perl local/select_from_uttlist.pl src_in_file target_file src_out_file" and die $!;
 }

open(FILE1,"$ARGV[0]") or die $!;
open(FILE2,"$ARGV[1]") or die $!;
open(FILE3,">$ARGV[2]") or die $!;


my %hash_id;
while(<FILE2>)
{
   chomp();
   my @contents = split(/\s+/);
   my $id = $contents[0];
   $hash_id{$id} = $_;
}

while(<FILE1>)
{
   chomp();
   my @contents = split(/\s+/);
   my $id = $contents[0];
   if (exists $hash_id{$id})
   {
       printf FILE3 ("%s\n",$hash_id{$id});
   }
}

close(FILE1);
close(FILE2);
close(FILE3);

