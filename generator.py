# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 16:47:03 2015

@brief:  Create sample sheet from TCGA metadata.json for Genomon.
@author: okada

$Id: generator.py 202 2017-07-10 09:48:38Z aokada $
$Rev: 202 $

@code
python generator.py {inputs} {type} {output_file} {option}
@endcode
"""

rev = " $Rev: 202 $"

import os
import sys
import bamtoimport
import create_samplesheet

def main():
    
    import argparse
    name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    # get args
    parser = argparse.ArgumentParser(prog = name)
    
    parser.add_argument("--version", action = "version", version = name + rev)
    parser.add_argument('inputs', help = "metadata file download from TCGA", type = str)
    parser.add_argument('type', help = "dna or rna", type = str)
    parser.add_argument('output_file', help = "output file, please input with format NAME.csv", type = str)
    
    parser.add_argument("-a", "--analysis_normal", help = "ノーマルサンプル,None,Noneを作成する", action='store_true', default = False)
    parser.add_argument("-e", "--enable_nopair", help = "ペアなしを許容する", action='store_true', default = False)
    parser.add_argument("-g", "--genomon_adapt", help = "genomonのペア（既存のサンプルシート）とmetadataのペアが異なるとき、Genomonを優先する", action='store_true', default = False)
    parser.add_argument("-l", "--large_controlpanel", help = "大きな一つのコントロールパネルを作成する", action='store_true', default = False)
    parser.add_argument("-s", "--set_controlpanel_length", help = "コントロールパネルの長さを指定する", type = int, default = 20, metavar="number_of_controlpanel")
    parser.add_argument("-u", "--unpair_is_normal", help = "unpairサンプルはノーマルサンプルとみなす(normalとして使用されていればこのフラグに関係なくノーマルとみなす)", action='store_true', default = False)

    parser.add_argument("-b", "--bam_import", help = "[fastq],[bam_tofastq] を [bam_import] に変換する。サンプルシートを更新したくない場合は --bam_import_only オプションを使用する", type = str, default = "", metavar="path_to_genomon_home")
    parser.add_argument("-bonly", "--bam_import_only", help = "[fastq],[bam_tofastq] を [bam_import] に変換する。このオプション使用時は入力ファイルは1つ限定で、サンプルシートを更新しない", type = str, default = "", metavar="path_to_genomon_home")

    parser.add_argument("-c", "--check_result_file", help = "check結果があれば指定する (紐づけはpathで行う) (under the development)", type = str, default = "", metavar="path_to_check_result_file")
    parser.add_argument("-n", "--no_result_is_ok", help = "resultファイルを指定するとき、結果がないファイルをOKとみなす (under the development)", action='store_true', default = False)
    parser.add_argument("-m", "--merge_normal", help = "ノーマルサンプルが複数ある時にマージするか (under the development)", action='store_true', default = False)
    
    args = parser.parse_args()
    
    inputs = []
    if args.bam_import != "":
        if args.bam_import_only != "":
            print ("[ERROR] set only one of bam_import and bam_import_only")
            return False

        for input in args.inputs.split(","):
            output = input + ".bam_import"
            if bamtoimport.bamtoimport(input, output, args.bam_import_only) == False:
                return False
                
            inputs.append(output)
    else:
        inputs = args.inputs.split(",")
        if args.bam_import_only != "":
            bamtoimport.bamtoimport(inputs[0], args.output_file, args.bam_import_only)
            return True
            
    options = {
        "analysis_normal": args.analysis_normal,
        "enable_nopair": args.enable_nopair,
        "large_controlpanel": args.large_controlpanel,
        "genomon_adapt": args.genomon_adapt,
        "set_controlpanel_length": args.set_controlpanel_length,
        
        "merge_normal": args.merge_normal,
        "check_result": os.path.exists(args.check_result_file),
        "no_result_is_ok": os.path.exists(args.check_result_file) and args.no_result_is_ok,
        "check_result_file": args.check_result_file,
    }
    print options

    if create_samplesheet.create_samplesheet(inputs, args.type, args.output_file, options) == False:
        print ("failure.")
        return False
    
    print ("success.")
    return True
    

if __name__ == "__main__":

    main()

