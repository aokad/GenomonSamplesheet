# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 16:47:03 2015

@brief:  GenomonPipelineで使用するサンプルシートを作成する
@author: okada

$Id: create_samplesheet.py 202 2017-07-10 09:48:38Z aokada $
$Rev: 202 $
"""
rev = " $Rev: 202 $"

import os
import pprint
import create_controlpanel

def create_samplesheet(inputs, gtype, output_file, options = {}):
    
    # path check
    for i in inputs:
        if os.path.exists(i) == False:
            print ("path is not exists. [inputs] " + i)
            return False
            
    # get path
    output_file = os.path.abspath(output_file)
    
    if os.path.exists(os.path.dirname(output_file)) == False:
        os.makedirs(os.path.dirname(output_file))
    
    # optionチェック
    options = set_options(options)
    
    # read inputs
    # sample名がkey
    path_loaded = {}
    sample_loaded = {
        "dna": { "mutation_call": AnalysisGroup("mutation_call"), "sv_detection": AnalysisGroup("sv_detection") },
        "rna": { "fusion": AnalysisGroup("fusion") }
    }
    
    # personが分からないとき、仮につけておく
    jane_list = {}  # genomon-data用
     
    for file_name in inputs:
        sept = ""
        if os.path.splitext(file_name)[1].lower() == ".csv":
            sept = ","
        elif os.path.splitext(file_name)[1].lower() == ".txt":
            sept = "\t"
        else:
            print ("Input output file path with format NAME.csv/ or .txt")
            continue
        
        f = open(file_name)
        mode = ""
        for text in f.readlines():
            text = text.rstrip()
            if text == "":
                continue
            if text.startswith("#"):
                continue
            
            if text.find("[") >= 0 and text.find("]") > 0:
                mode = text[text.find("[")+1: text.find("]")]
                continue
            
            cells = text.split(sept)
            if mode == "bam_import" or mode == "bam_tofastq" or mode == "fastq":
                if cells[0] in path_loaded:
                    print ("[WARNING] sample path is duplicate: [%s] %s" % (mode, cells[0]))
                path_loaded[cells[0]] = { "value": text.replace(cells[0] + sept, "", 1).replace("\t", ","), "mode": mode}
                
            elif ((gtype == "dna") and (mode == "mutation_call" or  mode == "sv_detection")) \
                or (gtype == "rna" and mode == "fusion"):
                
                person = "Jane-Doe-%04d" % (len(jane_list))
                if cells[0] in jane_list:
                    person = jane_list[cells[0]]
                else:
                    jane_list[cells[0]] = person
                    if cells[1].lower() != "none":
                        jane_list[cells[1]] = person
                        
                sample_loaded[gtype][mode].addMember(mode, cells[0], cells[1], person)
                
            elif mode == "metadata":
                if len(cells) < 3:
                    print ("[ERROR] invalid data: [%s] %s" % (mode, text))
                    return False
                
                for m in sample_loaded[gtype]:
                    sample_loaded[gtype][m].addMember("metadata", cells[0], cells[1], cells[2])
            else:
                continue
        f.close()
    
    # データチェック
    for mode in sample_loaded[gtype]:
        group = sample_loaded[gtype][mode]
            
        # pairの組み合わせを整理
        if group.marriage(options) == False:
            return False
        
        # パス確認
        if group.checkPath(path_loaded) == False:
            return False

    # write sample sheet
    f = open(output_file, "w")
    # file-path
    f.write(bamlist_totext(path_loaded))

    if options["debug"]:
        f_debug = open(output_file + ".debug", "w")
        f_debug.write(pprint.pformat(path_loaded))
        f_debug.write("\n")
    
    controlpanel_text = ""
    
    for mode in sample_loaded[gtype]:
        print ("*** %s ***" % (mode))
        
        group = sample_loaded[gtype][mode]
        if options["debug"]:
            f_debug.write(group.pformat())
        
        # make control_panel
        tumor_list = group.getSampleList(True, False)
        normal_list = group.getSampleList(False, False)
        control_panel = create_controlpanel.create_controlpanel(tumor_list, normal_list)
        if control_panel == None:
            continue
        
        if options["debug"]:
            f_debug.write(pprint.pformat(control_panel))
            f_debug.write("\n")
        
        # mutation / sv / fusion, etc
        f.write(sample_pair_totext(sample_loaded[gtype][mode], control_panel, options))
        
        # controlpanel        
        controlpanel_text += controlpanel_totext(control_panel, mode)

    if options["debug"]:        
        f_debug.close()
    
    # controlpanel
    f.write("[controlpanel]\n")
    f.write(controlpanel_text)

    f.close()
    
    return True
    
def bamlist_totext(path_loaded):
    text = ""
    pathes = {
        "bam_import": [],
        "bam_tofastq": [],
        "fastq": []
    }
    keys = sorted(path_loaded.keys())
    for key in keys:
        pathes[path_loaded[key]["mode"]].append([key, path_loaded[key]["value"]])
    
    for mode in ["bam_import", "bam_tofastq", "fastq"]:
        text += "[%s]\n" % mode
        for i in pathes[mode]:
            text += "%s,%s\n" % (i[0], i[1])
        
        text += "\n"
    return text
    
def sample_pair_totext(sample_loaded, control_panel, options):
    
    text = sample_loaded.totext(control_panel["tumor_controlpanel"], options)
    text += "\n"
    #print text
    return text

def controlpanel_totext(control_panel, mode):
    text = ""
    
    for obj in control_panel["controlpanel"]:
        text += "list_%s_%d,%s\n" % (mode, obj["index"], ",".join(obj["samples"]))
    return text

def set_options(options):
    default = {
        "enable_nopair": False,
        "analysis_normal": False,
        "large_controlpanel": False,
        "genomon_adapt": False,
        "set_controlpanel_length": 20,
        "debug": False,
        
        "merge_normal": False,
        "check_result": False,
        "no_result_is_ok": False,
        "check_result_file": "",
    }
    
    new_options = {}
    
    for key in default:
        if key in options:
            new_options[key] = options[key]
        else:
            new_options[key] = default[key]
    
    return new_options
    
class Pair:
    """A simple example class"""

    def __init__(self, name):
        self.name = name
        self.tumor = None
        self.pairs = []
        self.person = ""
        self.data_past = []
        self.data_meta = []
        
    def isPair(self):
        return len(self.pairs) > 0
        
    def isTumor(self):
        return self.tumor

    def isNormal(self):
        return self.tumor == False
    
    def getPair(self):
        if self.isNormal() == True:
            return None
        # tumorの場合、ペアは一つだけなので、配列の最初を返す
        return self.pairs[0]
        
    def getTumor(self, paired):
        if not self.isTumor():
            return None
            
        if paired and not self.isPair():
            return None
 
        return self.name

    def getNormal(self, paired):
        if not self.isNormal():
            return None
            
        if paired and not self.isPair():
            return None
            
        return self.name

    def getTumor_person(self, paired):
        if self.getTumor(paired) == None:
            return None
 
        return {"sample": self.getTumor(paired), "person": self.person}

    def getNormal_person(self, paired):
        if self.getNormal(paired) == None:
            return None
 
        return {"sample": self.getNormal(paired), "person": self.person}
        
    def checkPath(self, path_list):
        if not self.name in path_list:
            print ("[ERROR] sample path is not define: %s" % (self.name))
            return False
        
        return True
        
    def pformat(self):
        text = ""
        text += "name = %s\n" % (self.name)
        text += "person = %s\n" % (self.person)
        text += "tumor = %s\n" % (self.tumor)
        text += "normal = %s\n" % (pprint.pformat(self.pairs))
        text += "data_past = %s\n" % (pprint.pformat(self.data_past))
        text += "data_meta = %s\n" % (pprint.pformat(self.data_meta))
        return text
        
    def marriage(self, options):
        
        # メタデータを先に見る
        if len(self.data_meta) > 1:
            print ("[WARNING] metadata is duplicate. %s" % (self.name))
        if len(self.data_meta) > 0:
            self.tumor = self.data_meta[0]["tumor"]
            if self.data_meta[0]["pair"] != "":
                self.pairs.append(self.data_meta[0]["pair"])
            self.person = self.data_meta[0]["person"]
                
            if options["genomon_adapt"] == False:
                return True
                
        # gemononデータを次に見る
        # ペアなしサンプルがある場合、tumorフラグの組み合わせは以下のケースが考えられる
            
        # tumorの場合
        # [True] (通常)
        # [True, True] ----> pairが同じなら良いが、異なる場合は定義が被っているのでERRORを出す。
        # [True, False, unknown] --- > True
        
        # normalの場合
        # [False, unknown] ----> False
        # 
        # ペアなし
        # [unknown] ----> unpair_is_normalオプションに従うがデフォルトはペアなしのtumor       
        tumor = None
        pairs = []
        person = ""
        for items in self.data_past:
            if person != "" and person != items["person"]:
                print ("[DEBUG] person is miss set: %s, %s, %s" % (self.name, person, items["person"]))

            if items["tumor"] == True:
                tumor = True
                person = items["person"]
                if items["pair"] != "":
                    for pair in pairs:
                        if pair != items["pair"]:
                            # 異なるペア定義が同じサンプル名の時はエラー
                            print ("[ERROR] sample is duplicate: [%s] %s" % (self.mode, self.name))
                            return False
                    pairs.append(items["pair"])
                
            elif items["tumor"] == False:
                if tumor != True:                    
                    tumor = False
                    person = items["person"]
                    # normalの場合、異なるペア定義を許す
                    if items["pair"] != "":
                        pairs.append(items["pair"])
            else:
                if person == "":
                    person = items["person"]
                    
        if tumor == None:
            if self.tumor != None:
                tumor = self.tumor
            elif options["unpair_is_normal"]:
                tumor = False
            else:
                tumor = True
        
        self.tumor = tumor

        if len(pairs) > 0:
            self.pairs = []    
            self.pairs.extend(pairs)
        
        if self.person == "":
            self.person = person
            
        return True
        
class AnalysisGroup:
    """A simple example class"""

    def __init__(self, mode):
        self.mode = mode
        self.member = {}
        
    def getMember (self, sample):
        if not sample in self.member:
            self.member[sample] = Pair(sample)
        return self.member[sample]
        
    def addMember (self, mode, sample1, sample2, person):

        if mode == "fusion":
            self.getMember(sample1).data_past.append({"tumor": True, "pair": "", "person": person})
            
        elif mode == "mutation_call" or  mode == "sv_detection":
            if sample2.lower() == "none":
                self.getMember(sample1).data_past.append({"tumor": "unknown", "pair": "", "person": person})
            else:
                self.getMember(sample1).data_past.append({"tumor": True, "pair": sample2, "person": person})
                self.getMember(sample2).data_past.append({"tumor": False, "pair": sample1, "person": person})
            
        elif mode == "metadata":
            if sample1.lower() != "none" and sample2.lower() != "none":
                self.getMember(sample1).data_meta.append({"tumor": True, "pair": sample2, "person": person})
                self.getMember(sample2).data_meta.append({"tumor": False, "pair": sample1, "person": person})
            
            elif sample1.lower() != "none" and sample2.lower() == "none":
                self.getMember(sample1).data_meta.append({"tumor": True, "pair": "", "person": person})
            
            elif sample1.lower() == "none" and sample2.lower() != "none":
                self.getMember(sample2).data_meta.append({"tumor": False, "pair": "", "person": person})
            
    def marriage(self, options):
        # ペアの組み合わせを整理
        for pair in self.member:
            if self.member[pair].marriage(options) == False:
                return False
        
        return True
        
    def checkPath(self, path_loaded):
        for pair in self.member:
            if self.member[pair].checkPath(path_loaded) == False:
                return False
        return True
        
    def getSampleList(self, tumor, paired):
        
        # tumor/normal リストを取得する
        li = []
        keys = []
        for pair in self.member:
            if tumor:
                item = self.member[pair].getTumor_person(paired)
            else:
                item = self.member[pair].getNormal_person(paired)
            if item != None:
                key = "%s_%s" % (item["sample"], item["person"])
                if not key in keys:
                    li.append(item)
                    keys.append(key)
        return li

    def totext(self, mapp, options):
        
        #テキストに変換
        # tumorゾーン→normalゾーンと並べるために2つに分けておく
        text1 = "[%s]\n" % self.mode
        text2 = ""
        
        for pair in sorted(self.member.keys()):
            if options["enable_nopair"] == False and self.member[pair].isPair() == False:
                continue
            
            if self.member[pair].isTumor():
                text1 += "%s,%s,list_%s_%d\n" % (pair, self.member[pair].getPair(), self.mode, mapp[pair])
            else:
                if options["analysis_normal"] and self.member[pair].isPair():
                    # controlpanel用まで回ってしまうので、ペアのノーマルサンプルのみ
                    text2 += "%s,None,None\n" % (pair)
                    
        return text1 + text2
        
    def debug(self):
        print self.pformat()
    
    def pformat(self):
        text = "#######################\n"
        text += "[%s]\n" % (self.mode)
        text += "#######################\n"
        for pair in self.member:
            text += self.member[pair].pformat()
            text += "#######################\n"
        return text

        
if __name__ == "__main__":
    options = {
        "enable_nopair": True,
        "analysis_normal": True,
        "large_controlpanel": False,
        "genomon_adapt": False,
        "debug": False,
    }
    inputs = [
        "./example/template_case_controltxt",
        "./example/template_case_new.txt",
        "./example/template_case_prev.txt"
    ]
    create_samplesheet(inputs, "dna", "./output.csv", options)
