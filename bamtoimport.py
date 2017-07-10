# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 10:35:01 2015

@author: okada

$Id: bamtoimport.py 202 2017-07-10 09:48:38Z aokada $
$Rev: 202 $
"""
rev = " $Rev: 202 $"

import argparse
import sys
import os
import re

def bamtoimport(sample_sheet, output_file, genomon_root_dir):

    output_file = os.path.abspath(output_file)
    sample_sheet = os.path.abspath(sample_sheet)
    root_dir = os.path.abspath(genomon_root_dir)
    
    # make dir
    if (os.path.exists(os.path.dirname(output_file)) == False):
        os.makedirs(os.path.dirname(output_file))

    # file separations
    sep = ""
    ext = os.path.splitext(sample_sheet)[1]
    if ext.lower() == ".tsv":
        sep = "\t"
    elif ext.lower() == ".csv":
        sep = ","
    else:
        print ("bamtoimport:" + ext + " file is not support")
        return False

    ext_o = os.path.splitext(output_file)[0]
    
    output = ext_o + ext
    print "output file = %s" %(output)
     
    # read org data
    f = open(sample_sheet)
    data = f.readlines()
    f.close()
    
    txt_bam = ""
    txt_ext = ""
    
    for row in data:
        formatted = row.lower().strip().rstrip()
        if len(formatted) == 0:
            continue
        
        # header
        if formatted[0] == '[':
            mode = re.split('\[|\]', formatted)[1]
            if not mode in ['bam_tofastq', 'fastq', 'bam_import']:
                txt_ext += row
            continue
        
        cells = row.rstrip().split(sep)
        if (mode == 'bam_tofastq') or (mode == 'fastq'):
            txt_bam += "%s%s%s/bam/%s/%s.markdup.bam\n" % (cells[0], sep, root_dir, cells[0], cells[0])
        elif mode == 'bam_import':
            txt_bam += row
        else:
            txt_ext += row

    f = open(output_file, "w")
    f.write("[bam_import]\n")
    f.write(txt_bam + "\n")
    f.write(txt_ext + "\n")
    f.close()
    
    return True

if __name__ == "__main__":

    bamtoimport("./samplesheet.csv", "./output.csv", "/path/to/genomon")
