# actions:
# reads tables, chains, and rules from an input file
# for every table in the input file
#   for every chain in the table
#     create chain if chain does not exist in current iptables
#     for every rule in chain, check if the rule already exists in current iptables using string match
#       position of the rule is ignored, i.e. remove "-A" and "-I" from the rule before looking up for it in current iptables
#       if a rule already exist in the chain, skip the rule
#       otherwise, add the rule to the chain
# raise error if rules duplicate in a chain
#
# exit codes:
# 0: updated iptables without errors
# others: something went wrong, including all rules are already in place

import sys
import subprocess
import re
import getopt
import pprint
pp = pprint.PrettyPrinter(indent=4)

def runCommand(command):
   if options['quiet']=='false':
      print(command)
   try:
      out = subprocess.check_output(command, shell=True)
   except subprocess.CalledProcessError as exc:
      raise(exc)
   command_result = {'command': command, 'out': out}
   return(command_result)

def parseIptablesSave(content):
   # extract table blocks
   if isinstance(content, bytes):
      content = content.decode('utf-8')
   table_blocks = re.split("(?:^|\n)\*", content)
   table_blocks = filter2list(filter(lambda x: x.startswith("mangle\n") or x.startswith("raw\n") or
                                               x.startswith("filter\n") or x.startswith("nat\n"), table_blocks))
   tables = {}
   for t in table_blocks:
      lines = t.split('\n')
      # for each table, extract chains and rules
      chains = filter2list(filter(lambda x:x.startswith(":"), lines))
      chains = map2list(map(lambda x: x.split(" ")[0], chains))
      chains = map2list(map(lambda x: x[1:], chains))
      rules = filter2list(filter(lambda x:x.startswith("-"), lines))
      rules_content = map2list(map(lambda x:fix_content(x), rules))
#      print("rules:")
#      pp.pprint(rules)
#      print("rules_content:")
#      pp.pprint(rules_content)
      tables[lines[0]] = {"chains": chains, "rules": rules, "content": rules_content}
   return tables

def fix_content(line):
   content = line[3:]
   content = re.sub('[\"\']', '', content)
   content = re.sub(" -m comment --comment .+?( -[a-zA-Z] |$)", fix_content2, content)
   return content

def fix_content2(m):
   return m.group(1)

def map2list(input):
   output = list(input) if python_version>=3 else input
   return output

def filter2list(input):
   output = list(input) if python_version>=3 else input
   return output

def main(rule_filename):
   file = open(rule_filename, 'r')
   print("read file")
   tables_new = parseIptablesSave(file.read())
   save_result = runCommand("iptables-save")
   print("iptables-save")
   tables_existing = parseIptablesSave(save_result['out'])
   for t in tables_new:
      if not t in tables_existing:
         existing_table = {"chains": [], "rules": []}
      else:
         existing_table = tables_existing[t]
      new_table = tables_new[t]

      chains_to_add = filter2list(filter(lambda x:not x in existing_table['chains'], new_table['chains']))
      chain_commands = map2list(map(lambda x: 'iptables -t '+t+' -N '+x, chains_to_add))
      chain_command_results = map2list(map(lambda x:runCommand(x), chain_commands))

      rules_to_add = []
      for index, rule_content in enumerate(new_table['content']):
         if not rule_content in existing_table['content']:
            rules_to_add.append(new_table['rules'][index])
            pp.pprint(rule_content)

      rule_commands = map(lambda x: 'iptables -t '+t+' '+x, rules_to_add)
      if len(rule_commands)==0:
         print("all rules are already present")
         if options['nochange']=='false':
            sys.exit(2)
      rule_command_results = map2list(map(lambda x:runCommand(x), rule_commands))
      if len(rule_commands)>0:
         print("successfully updated iptables")

   if options['duplicate']=='false':
      new_save_result = runCommand("iptables-save")
      new_tables_existing = parseIptablesSave(new_save_result['out'])
      for t in new_tables_existing:
         rules = new_tables_existing[t]['content']
         l2 = []
         for r in rules:
            assert r not in l2, "duplicate rules found in current iptables \"" + t + "\" table:\n" + r
            l2.append(r)

def usage():
   print("python "+sys.argv[0] + " [-f|--filename] filename [-q|--quiet true/false] [-d|--duplicate true/false] [-c|nochange true/false]")
   print("generate the file with iptables-save, or created it following iptables-save output format")
   print("-q or --quiet true/false to toggle runtime information suppression, default is false")
   print("-d or --duplicate true/false to allow/disallow duplicate in rules, default is false")
   print("-c or --nochange true/false, when true, no change because all rules are already present is treated as a success, otherwise it's a failure. default is true")

try:
   opts, remainder = getopt.getopt(sys.argv[1:], 'f:q:d:c:', ['file=', 'quiet=', 'duplicate=', 'nochange='])
except:
   usage()
   sys.exit(2)
options = {'duplicate': 'false', 'quiet': 'false', 'nochange': 'true'}
for opt, arg in opts:
   if opt in ('-f', '--file'):
      options['file'] = arg
   elif opt in ('-q', '--quiet'):
      options['quiet'] = arg.lower()
   elif opt in ('-d', '--duplicate'):
      options['duplicate'] = arg.lower()
   elif opt in ('-c', '--nochange'):
      options['nochange'] = arg.lower()

if not 'file' in options:
   usage()
   sys.exit()

python_version=sys.version_info[0]
main(options['file'])

