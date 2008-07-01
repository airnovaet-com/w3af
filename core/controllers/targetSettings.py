'''
targetSettings.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

from core.controllers.configurable import configurable
import core.data.kb.config as cf

import core.data.parsers.urlParser as urlParser
from core.controllers.w3afException import w3afException
import time

# options
from core.data.options.option import option
from core.data.options.comboOption import comboOption
from core.data.options.optionList import optionList

cf.cf.save('targets', [] )
cf.cf.save('targetDomains', [] )
cf.cf.save('baseURLs', [] )

class targetSettings(configurable):
    '''
    A class that acts as an interface for the user interfaces, so they can configure the target
    settings using getOptions and SetOptions.
    '''
    
    def __init__( self ):
        # User configured variables
        #if cf.cf.getData('targets') == None:
        if True:
            # It's the first time I'm runned
            # Set the defaults in the config
            cf.cf.save('targets', [] )
            cf.cf.save('targetOS', 'unknown' )
            cf.cf.save('targetFramework', 'unknown' )
            cf.cf.save('targetDomains', [] )
            cf.cf.save('baseURLs', [] )
            cf.cf.save('sessionName', 'defaultSession' + '-' + time.strftime('%Y-%b-%d_%H-%M') )
        
        # Some internal variables
        self._operatingSystems = ['unknown','unix','windows']
        self._programmingFrameworks = ['unknown', 'php','asp','asp.net','java','jsp','cfm','ruby','perl']

                
    def getOptions( self ):
        '''
        @return: A list of option objects for this plugin.
        '''        
        d1 = 'A comma separated list of URLs'
        o1 = option('target', ','.join(cf.cf.getData('targets')), d1, 'list')
        
        d2 = 'Target operating system.'
        h2 = 'This setting is here to enhance w3af performance.'
        o2 = comboOption('targetOS', self._operatingSystems, d2, 'combo', help=h2)

        d3 = 'Target programming framework.'
        h3 = 'This setting is here to enhance w3af performance.'
        o3 = comboOption('targetFramework', self._programmingFrameworks, d3, 'combo', help=h3)
        
        ol = optionList()
        ol.add(o1)
        ol.add(o2)
        ol.add(o3)
        return ol
    
    
    def setOptions( self, optionsMap ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of getOptions().
        
        @parameter optionsMap: A dictionary with the options for the plugin.
        @return: No value is returned.
        ''' 
        targetUrls = optionsMap['target'].getValue()
        
        for targetUrl in targetUrls:
            if not targetUrl.count('file://') and not targetUrl.count('http://')\
            and not targetUrl.count('https://'):
                raise w3afException('Invalid format for target URL "'+ targetUrl + '", you have to specify the protocol (http/https/file).' )
        
        for targetUrl in targetUrls:
            if targetUrl.count('file://'):
                try:
                    f = open( targetUrl.replace( 'file://' , '' ) )
                except:
                    raise w3afException('Cannot open target file: ' + targetUrl.replace( 'file://' , '' ) )
                else:
                    for line in f:
                        targetUrls.append( line.strip() )
                    f.close()
                targetUrls.remove( targetUrl )
        
        # Save in the config, the target URLs, this may be usefull for some plugins.
        cf.cf.save('targets', targetUrls)
        cf.cf.save('targetDomains', [ urlParser.getDomain( i ) for i in targetUrls ] )
        cf.cf.save('baseURLs', [ urlParser.baseUrl( i ) for i in targetUrls ] )
        
        if targetUrls:
            sessName = [ urlParser.getDomain(x) for x in targetUrls ]
            sessName = '-'.join(sessName)
        else:
            sessName = 'noTarget'

        cf.cf.save('sessionName', sessName + '-' + time.strftime('%Y-%b-%d_%H-%M') )
        
        # Advanced target selection
        os = optionsMap['targetOS'].getValueStr()
        if os.lower() in self._operatingSystems:
            cf.cf.save('targetOS', os.lower() )
        else:
            raise w3afException('Unknown target operating system: ' + os)
        
        pf = optionsMap['targetFramework'].getValueStr()
        if pf.lower() in self._programmingFrameworks:
            cf.cf.save('targetFramework', pf.lower() )
        else:
            raise w3afException('Unknown target programming framework: ' + pf)

    def getName( self ):
        return 'targetSettings'
        
    def getDesc( self ):
        return 'Configure target URLs'
