# Created by Nicolas de Pineda Gutiérrez (Horned horn) 21/01/2018

from abc import ABCMeta, abstractmethod
from enum import Enum
import re

END_NUMBER_REGEX = re.compile("[0-9]+([\,\.][0-9]+)?\s*$")
DECIMALS = 3

class UnitType:

    def __init__( self ):
        self._multiples = {}
    
    def addMultiple( self, unit, multiple ):
        self._multiples[ multiple ] = unit;
        return self
        
    def getStringFromMultiple(self, value, multiple):
        return str(round(value / multiple, DECIMALS)) + self._multiples[multiple]
    
    def getString( self, value ):
        sortedMultiples = sorted(self._multiples, reverse=True)
        for multiple in sortedMultiples:
            if value > multiple/2:
                return self.getStringFromMultiple(value, multiple)
        return self.getStringFromMultiple( value, sortedMultiples[-1] )

DISTANCE = UnitType().addMultiple("m", 1).addMultiple( "km", 10**3 ).addMultiple( "cm", 10**-2).addMultiple( "mm", 10**-3).addMultiple( "µm", 10**-6).addMultiple( "nm", 10**-9)
AREA = UnitType().addMultiple( "m^2", 1 ).addMultiple( "km^2", 10**6 ).addMultiple( "cm^2", 10**-4).addMultiple( "mm^2", 10**-6)
VOLUME = UnitType().addMultiple( "L", 1 ).addMultiple( "mL", 10**-3 )
ENERGY = UnitType().addMultiple( "J", 1 ).addMultiple( "TJ", 10**12 ).addMultiple( "GJ", 10**9 ).addMultiple( "MJ", 10**6 ).addMultiple( "kJ", 10**3 ).addMultiple( "mJ", 10**-3 ).addMultiple( "µJ", 10**-6 ).addMultiple( "nJ", 10**-9 )
FORCE = UnitType().addMultiple( "N", 1 ).addMultiple( "kN", 10**3 ).addMultiple( "MN", 10**6 )
TORQUE = UnitType().addMultiple( "N*m", 1 )
VELOCITY = UnitType().addMultiple("m/s", 1).addMultiple( "km/s", 10**3 ).addMultiple( "km/h", 3.6 )
MASS = UnitType().addMultiple( "g", 1 ).addMultiple( "kg", 10**3 ).addMultiple( "t", 10**6 ).addMultiple( "mg", 10**-3 ).addMultiple( "µg", 10**-6 )
TEMPERATURE = UnitType().addMultiple( "C", 1 )
PRESSURE = UnitType().addMultiple( "atm", 1 )

class Unit:
    def __init__( self, unitType, toSIMultiplication, toSIAddition ):
        self._unitType = unitType
        self._toSIMultiplication = toSIMultiplication
        self._toSIAddition = toSIAddition
    
    def toMetric( self, value ):
        return self._unitType.getString( ( value + self._toSIAddition ) * self._toSIMultiplication)
    
    @abstractmethod
    def convert( self, message ): pass

#NormalUnit class, that follow number + unit name.
class NormalUnit( Unit ):
    def __init__( self, regex, unitType, toSIMultiplication, toSIAddition = 0 ):
        super( NormalUnit, self ).__init__(unitType, toSIMultiplication, toSIAddition)
        self._regex = re.compile( regex + "(?![a-z])")
    
    def convert( self, message ):
        originalText = message.getText()
        iterator = self._regex.finditer( originalText )
        replacements = []
        for find in iterator:
            numberResult = END_NUMBER_REGEX.search( originalText[ 0 : find.start() ] )
            if numberResult is not None:
                repl = {}
                repl[ "start" ] = numberResult.start()
                repl[ "text"  ] = self.toMetric( float( numberResult.group() ) ) 
                repl[ "end" ] = find.end()
                replacements.append(repl)
        if len(replacements)>0:
            lastPoint = 0
            finalMessage = ""
            for repl in replacements:
                finalMessage += originalText[ lastPoint: repl[ "start" ] ] + repl[ "text" ]
                lastPoint = repl["end"]
            finalMessage += originalText[ lastPoint : ]
            message.setText(finalMessage)

# Class containing a string, for the modificable message, and a boolean
# to indicate if the message has been modified
class ModificableMessage:
    
    def __init__(self, text):
        self._text = text
        self._modified = False
        
    def getText(self):
        return self._text
    
    def setText(self, text):
        self._text = text
        self._modified = True
        
    def isModified(self):
        return self._modified
        
units = []

#Distance units
units.append( NormalUnit("in(ch(es)?)?|\"|''", DISTANCE, 0.0254) )	#inch
units.append( NormalUnit("f(oo|ee)?t|'", DISTANCE, 0.3048) )		#foot
units.append( NormalUnit("mi(les?)?", DISTANCE, 1609.344) )			#mile

#Area
units.append( NormalUnit("in(ch(es)?)? ?(\^2|squared)", DISTANCE, 0.00064516) )	#inch squared
units.append( NormalUnit("f(oo|ee)?t ?(\^2|squared)", DISTANCE, 0.092903) )		#foot squared
units.append( NormalUnit("mi(les?)? ?(\^2|squared)", DISTANCE, 2589990) )		#mile squared
units.append( NormalUnit("acres?", AREA, 4046.8564224 ) )						#acre
#Volume
units.append( NormalUnit( "pints?|pt|p", VOLUME, 0.473176 ) )	#pint
units.append( NormalUnit( "quarts?|qt", VOLUME, 0.946353 ) )	#quart
units.append( NormalUnit( "gal(lons?)?", VOLUME, 3.78541 ) )	#galon

#Energy
units.append( NormalUnit("ft( |\*)?lbf?|foot( |-)pound", ENERGY, 1.355818) )	#foot-pound

#Force
units.append( NormalUnit("pound( |-)?force|lbf", FORCE, 4.448222) )	#pound-force

#Torque
units.append( NormalUnit("Pound(-| )?foot|lbf( |\*)?ft", TORQUE, 1.355818) )	#pound-foot

#Velocity
units.append( NormalUnit("miles? per hour|mph", VELOCITY, 0.44704) )	#miles per hour

#Mass
units.append( NormalUnit( "ounces?|oz", MASS, 28.349523125 ) )	#ounces
units.append( NormalUnit( "pounds?|lbs?", MASS, 453.59237 ) )	#pounds

#Temperature
units.append( NormalUnit("º?F", TEMPERATURE, 5/9, -32 ) )	#Degrees freedom
#Pressure
units.append( NormalUnit( "pounds?((-| )?force)? per square in(ch)?|lbf\/in\^2|psi", PRESSURE, 0.068046 ) ) #Pounds per square inch
 
#Processes a string, converting freedom units to science units.
def process(message):    
    modificableMessage = ModificableMessage(message)
    for u in units:
        u.convert(modificableMessage)
    if modificableMessage.isModified():
        return modificableMessage.getText()
