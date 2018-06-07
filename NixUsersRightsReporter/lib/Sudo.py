#!/usr/bin/python
#
# This program parses a sudoers file and can be used to test who has 
# what access
#
# Author: Joel Heenan 30/09/2008
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.



import re,grp,socket,sys,os,commands
from optparse import OptionParser

try:
    import netgroup
    netgroupSupport = True
except:
    netgroupSupport = False

class SudoCmnd:
    def __init__(self,runas,passwd,command,sp):
        self.runas = runas
        self.passwd = passwd
        self.command = command
        self.sp = sp

    def __repr__(self):
        commands = []
        for cmndAlias in self.sp.cmndAliases:
            if(cmndAlias == self.command):
                commands = self.sp.cmndAliases[cmndAlias]
                
        if(self.passwd):
            str = "(%s) %s\n" % (self.runas, self.command)
        else:
            str = "(%s) NOPASSWD: %s" % (self.runas, self.command)
        for command in commands:
            str += "\t%s\n" % command
        return str

    def matchCommand(self,command):
        if(command == self.command):
            return True
        for cmndAlias in self.sp.cmndAliases:
            if(cmndAlias == self.command):
                return self.sp.matchCmndAlias(self.sp.cmndAliases[cmndAlias],command)
        return self.sp.matchCmndAlias([self.command],command)

class SudoRule:
    def __init__(self,user,server,command,sp):
        self.user = user
        self.server = server
        self.command = command
        self.sp = sp

    def __repr__(self):
        return "%s %s %s" % (self.user,self.server,self.command)

    def matchUser(self,user):
        if(user == self.user):
            return True
        for userAlias in self.sp.userAliases:
            if(userAlias == self.user): #I'm a user alias
                return self.sp.matchUserAlias(self.sp.userAliases[userAlias],user)
        return self.sp.matchUserAlias([self.user],user)

    def matchHost(self,host):
        if(host == self.server):
            return True
        for hostAlias in self.sp.hostAliases:
            if(hostAlias == self.server): #I'm a host alias
                return self.sp.matchHostAlias(self.sp.hostAliases[hostAlias],host)
        return self.sp.matchHostAlias([self.server],host)

class SudoersParser:
    def __init__(self):
        self.netgroupWarning = 'netgroup syntax used in file but no python netgroup support. Install the python netgroup module for support'

    def parseFile(self,file):
        self.hostAliases  = {}
        self.userAliases  = {}
        self.cmndAliases  = {}
        self.rules        = []
        lines = file.readlines()
        lines = self._collapseLines(lines)

        defaultsRE  = re.compile("^\s*Defaults")
        hostAliasRE = re.compile("^\s*Host_Alias")
        userAliasRE = re.compile("^\s*User_Alias")
        cmndAliasRE = re.compile("^\s*Cmnd_Alias")

        for line in lines:
            if(defaultsRE.search(line)):
                # don't currently do anything with these
                continue
            if(hostAliasRE.search(line)):
                self.hostAliases.update(self._parseAlias(line,"Host_Alias"))
                continue
            if(userAliasRE.search(line)):
                self.userAliases.update(self._parseAlias(line,"User_Alias"))
                continue
            if(cmndAliasRE.search(line)):
                self.cmndAliases.update(self._parseAlias(line,"Cmnd_Alias"))
                continue

            rule = self._parseRule(line)
            if(rule):
                self.rules.append(rule)

    # what commands can a user run on a particular host?
    # note: we assume that the current user/group environment is the
    # same as the host 
    def getCommands(self,user,host="localhost"):
        if(host=="localhost" or host==None):
            host=socket.gethostname()

        commands = []

        match = False
        for rule in self.rules:
            if(rule.matchUser(user) and rule.matchHost(host)):
                match = True
                for cmnd in rule.command:
                    commands.append(cmnd)
        #if(not match):
            #commands.append("No Sudo Matches")

        return commands

    def canRunCommand(self,user,command,host="localhost"):
        """
        Can the user run this particular command?
        """
        if(host=="localhost" or host==None):
            host=socket.gethostname()
        for rule in self.rules:
            if(rule.matchUser(user) and rule.matchHost(host)):
                for cmnd in rule.command:
                    if(cmnd.matchCommand(command)):
                        print "User %s can run command %s" % (user,command)
                        return True
        print "User %s can not run command %s" % (user,command)
        return False
            
    # given the contents of a user alias, see if it matches a particular user
    def matchUserAlias(self,userAlias, user):
        for entry in userAlias:
            if(entry == user):
                return True
            elif(entry[0] == "%"):
                return self._userInGroup(entry[1:],user)
            elif(entry[0] == "+"):
                return self._userInNetgroup(entry[1:],user)
        return False

    def matchHostAlias(self,hostAlias,host):
        for entry in hostAlias:
            if(entry == "ALL"):
                return True
            elif(entry.find(host) == 0):
                return True
            elif(entry[0] == '+'):
                return self._hostInNetgroup(entry[1:],host)
        return False

    def matchCmndAlias(self,cmndAlias,command):
        match = False
        for entry in cmndAlias:
            negate = False
            if(entry[0] == "!"):
                negate = True
                entry = entry[1:]
            if(entry.find(command) == 0):
                if(negate):
                    return False
                match = True
            if(os.path.normpath(entry) == os.path.dirname(command)):
                if(negate):
                    return False
                match = True
            if(entry == "ALL"):
                match = True
        return match
                
    def _userInGroup(self,group,user):
        try:
            (gr_name, gr_passwd, gr_gid, gr_mem) = grp.getgrnam(group)
        except KeyError:
#            print "warning: group %s was not found" % group
            return False
        if(user in gr_mem):
            return True
    
    def _userInNetgroup(self,group,searchUser):
        if(netgroupSupport):
            return netgroup.innetgr(group,user=searchUser)
        else:
            print self.netgroupWarning
    
    def _hostInNetgroup(self,searchNetgroup,searchHost):
        if(netgroupSupport):
            return netgroup.innetgr(searchNetgroup,host=searchHost)
        else:
            print self.netgroupWarning
    
    def _parseAlias(self,line,marker):
        res = {}
    
        aliasRE = re.compile("\s*%s\s*(\S+)\s*=\s*((\S+,?\s*)+)" % marker)
        m = aliasRE.search(line)
        if(m):
            alias = str(m.group(1))
            nodes = str(m.group(2)).split(",")
            nodes = [ node.strip() for node in nodes ]
            res[alias] = nodes

        return res

    def _parseRule(self,line):
        ruleRE = re.compile("\s*(\S+)\s*(\S+)\s*=\s*(.*)")
        
        runasRE = re.compile("^\s*\((\S+)\)(.*)")
        m = ruleRE.search(line)
        if(m):
            user = str(m.group(1))
            host = str(m.group(2))
            parsedCommands = []
            
            cmnds = str(m.group(3)).split(",")
            cmnds = [ cmnd.strip() for cmnd in cmnds ]
            for cmnd in cmnds:
                unparsed = cmnd
                m = runasRE.search(unparsed)
                if(m):
                    runas = str(m.group(1))
                    unparsed = str(m.group(2))
                else:
                    runas = "ANY"
                pos = unparsed.find("NOPASSWD:")
                if(pos > -1):
                    passwd = False
                    unparsed = unparsed[pos+len("NOPASSWD:"):]
                else:
                    passwd = True
                unparsed = unparsed.strip()

                parsedCommands.append(SudoCmnd(runas,passwd,unparsed,self))
            
            return SudoRule(user,host,parsedCommands,self)

    def _collapseLines(self,lines):
        res = []
        currentline = ""
        
        for line in lines:
            if(line.rstrip()[-1:] == "\\"):
                currentline += line.rstrip()[:-1]
            else:
                currentline += line
                res.append(currentline)
                currentline = ""

        return res

def createParser():
    parser = OptionParser(usage="%prog [options] -u user")
    parser.add_option("-f","--file",dest="sudoersFile",metavar="FILE",
                      help="sudoers file to parser (default /etc/sudoers)",default="/etc/sudoers")
    parser.add_option("-s","--host",dest="host",metavar="HOST",
                      help="host (default is this host)")
    parser.add_option("-u","--user",dest="user",metavar="USER",
                      help="username to lookup (mandatory)")
    parser.add_option("-c","--command",dest="command",metavar="COMMAND",
                      help="Instead of printing all commands, test whether this command can be run")
    return parser

def main():
    parser = createParser()
    (options,args) = parser.parse_args()
    if(not options.user):
        parser.print_help()
        sys.exit(1)
        
    sp = SudoersParser()
    sp.parseFile(options.sudoersFile)

    if(options.command):
        cmnd = options.command
        if(options.command.find('/') == -1):
            cmnd = commands.getstatusoutput('which %s' % options.command.split(" ")[0])[1]
        elif(options.command[0] != '/'):
            cmnd = os.path.normpath(os.path.join(os.getcwd(),options.command))
        if(sp.canRunCommand(options.user,cmnd,options.host)):

            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sp.getCommands(options.user,options.host)

if(__name__ == "__main__"):
    main()
