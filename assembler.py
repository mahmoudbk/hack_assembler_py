
table = {
} #initializing the table 

#populating the table with predefined symbles (R0..R15 ..Etc)

for i in range(16):
    table[f"R{i}"] = i 

#adding KBD, SCREEN, SP,LCL,ARG,THIS,THAT
more_predefined_symbols = {
    'SCREEN':16384,
    'KBD':24576,
    'SP':0,
    'LCL':1,
    'ARG':2,
    'THIS':3,
    'THAT':4
}
#adding the rest of predefined symbols to the table
table.update(more_predefined_symbols)


desttable = {
    "":"000",
    "M":bin(1 & 0xFFFF)[2:].zfill(3),
    "D":bin(2 & 0xFFFF)[2:].zfill(3),
    "MD":bin(3 & 0xFFFF)[2:].zfill(3),
    "A":bin(4 & 0xFFFF)[2:].zfill(3),
    "AM":bin(5 & 0xFFFF)[2:].zfill(3),
    "AD":bin(6 & 0xFFFF)[2:].zfill(3),
    "AMD":bin(7 & 0xFFFF)[2:].zfill(3)
}

jmptable = {
    "":"000",
    "JGT":bin(1 & 0xFFFF)[2:].zfill(3),
    "JEQ":bin(2 & 0xFFFF)[2:].zfill(3),
    "JGE":bin(3 & 0xFFFF)[2:].zfill(3),
    "JLT":bin(4 & 0xFFFF)[2:].zfill(3),
    "JNE":bin(5 & 0xFFFF)[2:].zfill(3),
    "JLE":bin(6 & 0xFFFF)[2:].zfill(3),
    "JMP":bin(7 & 0xFFFF)[2:].zfill(3)
}
ctable = {
    #a=0
    "0":["0","101010"],
    "1":["0","111111"],
    "-1":["0","111010"],
    "D":["0","001100"],
    "A":["0","110000"],
    "!D":["0","001101"],
    "!A":["0","110001"],
    "-D":["0","001111"],
    "-A":["0","110011"],
    "D+1":["0","011111"],
    "A+1":["0","110111"],
    "D-1":["0","001110"],
    "A-1":["0","110010"],
    "D+A":["0","000010"],
    "D-A":["0","010011"],
    "A-D":["0","000111"],
    "D&A":["0","000000"],
    "D|A":["0","010101"],
    #a=1 
    "M":["1","110000"],
    "!M":["1","110001"],
    "-M":["1","110011"],
    "M+1":["1","110111"],
    "M-1":["1","110010"],
    "D+M":["1","000010"],
    "D-M":["1","010011"],
    "M-D":["1","000111"],
    "D&M":["1","000000"],
    "D|M":["1","010101"]



}


#we import sys to retrieve the command line argument (which should be the assembly file )
import sys 

#not allow more than one argument nor less than one 


if len(sys.argv)>2:
    print("assemble one file at a time")
    sys.exit(1)
elif len(sys.argv)==1:
    print("you need to include the file to assemble as follows : python assembler.py filename.asm")
    sys.exit(1)

filename = sys.argv[1]

#check the file extension (must be .asm)
extension = filename.split(".")[-1]
if extension.lower()!="asm":
    print("assemble only .asm files example : add.asm")
    sys.exit(1)

#check if file exists in the directory and read it line by line
try:
    with open(filename,"r") as assemblyfile:
        data = assemblyfile.readlines()  #extract data line by line
    assemblyfile.close()
except Exception as e :
    print(e)
    sys.exit(1)

#naming the output file (filename.hack)
output_file = f"{filename.split('.')[0]}.hack" 

#the function to extract (xxx) label symbols using regex
import re 
def label_symbol(text_line):
    pattern = r'\((.*?)\)'
    match = re.search(pattern, text_line)
    if match:
        content_inside_parentheses = match.group(1)
        return content_inside_parentheses
    return None 


#ignores comments 
def clean_line(text_line):
    line = text_line.split("//")[0].strip()
    if line :
        return line 

    return None

#converting from decimal to 15-bit binary 
def decimal_to_15bit_binary(decimal_number):
    binary_representation = bin(decimal_number & 0xFFFF)[2:].zfill(15)
    return binary_representation

#check if is integer as in @15
def is_integer(word):
    word = word.strip()
    try:
        int(word)
        return True 
    except:
        return False


def translate_a_instruction(instruction,var_num):
    
    inst  = instruction.split('@')[-1]

    #check if it's predefined extract value from table otherwise its a variable 
    
    if is_integer(inst):#example @32 or something 
        bit_rep = decimal_to_15bit_binary(int(inst))

        return (f"0{bit_rep}",var_num)

    if inst in table:

        bit_rep = decimal_to_15bit_binary(table[inst])
        return (f"0{bit_rep}",var_num)

   
    #new variable
    table[inst] = var_num
    bit_rep = decimal_to_15bit_binary(var_num)
 
    var_num+=1 
    return (f"0{bit_rep}",var_num)
    

def translate_c_instruction(instruction):
    instruction = instruction.strip()
    jmp = bin(0 & 0xFFFF)[2:].zfill(3)
    dest = bin(0 & 0xFFFF)[2:].zfill(3)
    if ";" in instruction:
        
        jmp_cont = instruction.split(';')[-1].strip()
        jmp = jmptable[jmp_cont].strip()
        
    if "=" in instruction :
        dest_cont = instruction.split('=')[0].strip()
        
       

        dest = desttable[dest_cont].strip()
        
    c_cont = instruction
    if "=" in c_cont :
        c_cont = instruction.split('=')[1].strip()
    if ";" in c_cont:
            c_cont = c_cont.split(';')[0].strip()
    comp = ctable[c_cont]

    return f"111{comp[0].strip()}{comp[1].strip()}{dest}{jmp}"



def first_pass(lines):
    clean_data  = []
    num_lines = -1
    
    #we read line by line ignoring comments and adding (xxx) 
    #typg of instructions in our table in pairs (xxx,address) wher address is the number of instruction -
    #following the (xxx)

     #keep track of the number of lines 
    for i in range(len(lines))  :
        if clean_line(lines[i]):
            line = clean_line(lines[i])
            clean_data.append(line)
          
            if "(" in line :
                table[label_symbol(line)] = num_lines+1 #number of next line
                continue
            num_lines += 1
                
    return clean_data




def second_pass(lines):
    #we scan the entire program again 
    #if the instruction is @symbol,we try find it in the symbole table if found we translate it and write it 
    #to filename.hack otherwise it's a variable that follows n 
    
    #recompile every time (empty the file) and override the previous file 
    with open(output_file,"w") as file:
        file.write("")
    n=16 #default start address of the assembly variables 
    
    
    with open(output_file,"a+") as file:
        for line in lines:
            if "@" in line:
                inst, var_num = translate_a_instruction(line, n)
                inst += "\n"
                n = var_num
                file.write(inst)
            elif "(" in line:
                pass 
            else:
                inst = translate_c_instruction(line)
                inst += "\n"
                file.write(inst)


clean_data = first_pass(data)
second_pass(clean_data)
