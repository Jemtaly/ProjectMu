grammar mu;
music
    : nls groups final nls EOF
    ;
groups
    : group (';' nlp group)*
    ;
group
    : mod spp mtr spp bmp nlp passages
    ;
passages
    : passage (',' nlp passage)*
    ;
passage
    : measures
    ;
measures
    : measure (nls measure)*
    ;
measure
    : elements sps '|'
    ;
elements
    : element (sps element)*
    ;
element
    : note time
    | angled
    | rat angled
    | rat braced
    ;
final
    : ':' nlp nums
    | '|'
    ;
mod
    : sao '=' aao
    ;
mtr
    : num '/' num
    ;
bmp
    : num
    ;
rat
    : '[' num (':' num)? ']'
    ;
angled
    : '<' elements '>'
    ;
braced
    : '{' elements '}'
    ;
note
    : sao
    | rest
    | tie
    ;
sao
    : accid solfa octav
    ;
aao
    : alpha accid octav
    ;
time
    : '/'* '.'*
    ;
accid
    : ('b'+ | '#'+ | '@')?
    ;
octav
    : ('\''+ | ','+)?
    ;
nums
    : num (spp num)*
    ;
num
    : ('1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9') ('0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9')*
    ;
alpha
    : 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G'
    ;
solfa
    : '1' | '2' | '3' | '4' | '5' | '6' | '7'
    ;
rest
    : '0'
    ;
tie
    : '-'
    ;
spp
    : ' '+
    ;
sps
    : ' '*
    ;
nlp
    : sps (('\n' | '\r') sps)+
    ;
nls
    : sps (('\n' | '\r') sps)*
    ;
