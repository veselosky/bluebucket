itemtype: Item/Page/Article
guid: ab2a947c-0557-4c5d-a535-5b8c5a875cdf
atom_id: tag:www.webquills.net,2008:/scroll//1.23
ID: 33
Created: 2008-05-26 12:07:37  
updated: 2008-05-26 12:07:37  
Published: 2008-05-26 12:00:57  
Tags: hash, perl, slice
category: web-development/perl
slug: perl-5-hash-slices-can-replace
Title: Perl 5: Hash slices can replace loops

# Perl 5: Hash slices can replace loops

How many times have you written a `for` loop to do something simple with a hash
and thought, there must be a better way to do this? Using hash slices instead of
simple loops can save you lines of code and execution time.

A *hash slice* is a syntax for accessing the values of multiple keys of a hash
in a single statement. It is a succinct and efficient technique, but it is also
one of those collections of punctuation that give Perl a reputation as a
write-only language. Once you have learned it, however, you will feel much more
clever! Here are a few examples of how I use hash slices to make my code shorter
and faster. (Note that you can also slice arrays, but today we are just talking
about hashes.)

## Basic hash slice syntax
You perform a hash slice by using a list as a hash index, rather than a scalar
value, and preceding with the `@` sigil rather than the `$` sigil you would use
to get a scalar value.
    
    my %number_for = (one => 1, two => 2, three => 3);
    # Regular access to scalar key
    print $number_for{one}; # 1
    # Hash slice accesses multiple keys. Note the '@'
    print @number_for{qw(one two three)}; # 123
    # This also works
    print @number_for{'one','two','three'}; # 123
    
A cautionary note: notice how the scalar index uses a bare word as the key. Perl
gives you the quoting for free in this case. With a slice, Perl doesn't help, so
you have to do the quoting yourself.
    
## Merging two hashes
Since hash slices can be lvalues, they can be used to merge one hash into
another. A common example is when you get configuration information from more
than one source, but you want to consolidate it to look up in just one place.

    my %your_numbers = (two => 2, four => 4, six => 6);
    # I get all your numbers! 
    # (And your number will override mine if they differ)
    @number_for{keys %your_numbers} = values %your_numbers;
    print sort values %number_for; # 12346


## Accessing keys in a particular order
Here is a common thing you run into in web development. You have received input
from a web form and validated it. (You *have* validated it, right?) The data
lives in a hash, and you want to store it in a database. You have your SQL
statement all prepared, but it requires that the values be bound in exact column
order. Unfortunately, the `values` function cannot be relied upon to return the
values in the order you want. (And besides, you don't want to store the value of
the submit button!)

    # get valid data from your validation code
    my %validated = %number_for;
    # Columns of your table, in order needed by your SQL
    my @columns = qw(six one three);
    # Get the bind values with a slice
    my @bind = @validated{@columns}; # 6,1,3
    

## Accessing values sorted by keys
Say you want to sort a hash by its keys, and then use the values in that sorted
order. Using the above data, perhaps we want to print numbers in alphabetical
order.

    print @number_for{sort keys %number_for}; # 41632


## Slicing a hash reference
Eventually you will find yourself with a reference to a hash, and you will
discover that the above syntax does not work. You may try three or four
different combinations of curlies and arrows that just generate errors. Don't
give up! You *can* slice a hashref! First, let's review using a hashref to get
at scalar values.

    my $num_for = \%number_for;
    # Common syntax for dereferencing and getting a scalar index
    print $num_for->{one}; # 1
    # Alternate syntax, the lazy way:
    print $$num_for{two}; # 2
    # Alternate syntax, the explicit way
    print ${$num_for}{six}; # 6

The key to slicing a reference to a hash is to use the alternate syntax shown
above, replacing the initial `$` sigil with `@`.
    
    # The lazy way:
    print @$num_for{@columns}; # 613
    # The explicit way:
    print @{$num_for}{@columns}; # 613

Note the distinct absence of the "arrow" syntax. The arrow implies a scalar, and
we want a list.

## Powerful syntax
The hash slice is an advanced syntax demonstrating Perl's concision and
expressiveness. Now you should be able to recognize it when you see it, and
hopefully apply it to your own projects to save time and space. (But remember,
use your Perl superpowers only for Good, never for Evil!)

For a semi-regular diet of great Perl programming tips, [subscribe to the
Webquills.net feed](http://feeds.feedburner.com/Webquills) or [get Webquills.net
via
email](http://www.feedburner.com/fb/a/emailverifySubmit?feedId=929839&loc=en_US). 
