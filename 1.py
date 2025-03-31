import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSlot

from Thermo2StateCalc import Ui_frmTwoStateCalculator
from UnitConversion import UC

from pyXSteam.XSteam import XSteam
from scipy.optimize import fsolve


###############################################################################
#   HELPER CLASSES
###############################################################################

class thermoState:
    """
    A container for any thermodynamic state, using pyXSteam to compute
    missing properties from any two specified properties (p, T, h, u, s, v, x).
    We add some safety checks and debug prints to avoid out-of-range calls.
    """
    def __init__(self):
        self.steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS)
        self.region = "saturated"
        self.p = None
        self.t = None
        self.v = None
        self.u = None
        self.h = None
        self.s = None
        self.x = None

    def computeProperties(self):
        """Compute final properties from (p,t,region,x, etc.) after setState."""
        if self.region == "two-phase":
            uf = self.steamTable.uL_p(self.p)
            ug = self.steamTable.uV_p(self.p)
            hf = self.steamTable.hL_p(self.p)
            hg = self.steamTable.hV_p(self.p)
            sf = self.steamTable.sL_p(self.p)
            sg = self.steamTable.sV_p(self.p)
            vf = self.steamTable.vL_p(self.p)
            vg = self.steamTable.vV_p(self.p)

            self.u = uf + self.x * (ug - uf)
            self.h = hf + self.x * (hg - hf)
            self.s = sf + self.x * (sg - sf)
            self.v = vf + self.x * (vg - vf)
        else:
            # Subcooled or superheated or saturated
            self.u = self.steamTable.u_pt(self.p, self.t)
            self.h = self.steamTable.h_pt(self.p, self.t)
            self.s = self.steamTable.s_pt(self.p, self.t)
            self.v = self.steamTable.v_pt(self.p, self.t)

            if self.region == "super-heated vapor":
                self.x = 1.0
            elif self.region == "sub-cooled liquid":
                self.x = 0.0

    def setState(self, prop1, prop2, val1, val2, SI=True):
        """
        Sets the thermodynamic state, given two property names (e.g., 'p','t')
        and their numeric values in either SI or English units.
        We do minimal checks for valid ranges to avoid XSteam crashes.
        """
        # Switch XSteam to correct units
        self.steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS if SI else XSteam.UNIT_SYSTEM_FLS)

        def checkPressure(pbar):
            if pbar <= 0.0:
                raise ValueError(f"Invalid pressure {pbar:.3f} bar (must be > 0).")
            if pbar > 300.0:
                raise ValueError(f"Pressure {pbar:.3f} bar above XSteam limit (~300).")

        def checkTemperature(tC):
            if tC < 0.0:
                raise ValueError(f"Temperature {tC:.2f} C below 0 is not supported.")
            if tC > 600.0:
                raise ValueError(f"Temperature {tC:.2f} C above 600 might crash XSteam.")

        print(f"[DEBUG] setState called with: {prop1}={val1}, {prop2}={val2}, SI={SI}")

        prop1 = prop1.lower().strip()
        prop2 = prop2.lower().strip()

        # ------------------- EXAMPLE: p–t or t–p -------------------
        if ('p' in [prop1, prop2]) and ('t' in [prop1, prop2]):
            if prop1 == 'p':
                self.p = val1
                self.t = val2
            else:
                self.p = val2
                self.t = val1

            checkPressure(self.p)
            checkTemperature(self.t)

            tsat = self.steamTable.tsat_p(self.p)
            if abs(self.t - tsat) < 0.0001:
                self.region = "two-phase"
                self.x = 0.5
            elif self.t > tsat:
                self.region = "super-heated vapor"
            else:
                self.region = "sub-cooled liquid"

            self.computeProperties()
            return

        # ------------------- EXAMPLE: p–x or x–p -------------------
        if ('p' in [prop1, prop2]) and ('x' in [prop1, prop2]):
            if prop1 == 'p':
                self.p = val1
                self.x = val2
            else:
                self.p = val2
                self.x = val1

            checkPressure(self.p)
            # clamp x
            if self.x < 0.0: self.x = 0.0
            if self.x > 1.0: self.x = 1.0

            self.region = "two-phase"
            self.t = self.steamTable.tsat_p(self.p)
            checkTemperature(self.t)
            self.computeProperties()
            return

        # ----- etc. for other combos: p–h, p–v, t–h, t–v, v–h, v–u, etc. -----
        # You can paste the rest of your logic from the single-state code here
        # as needed, making sure to do checks/clamps. This is just a sample.

        # If none matched, raise:
        raise ValueError(f"Property combo ({prop1}, {prop2}) not implemented yet.")


###############################################################################
#   MAIN WINDOW
###############################################################################
class main_window(QWidget, Ui_frmTwoStateCalculator):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.currentUnits = 'SI'  # track which system is active
        self.setupSignals()
        self.show()

        # These hold the "current labels" for each property in SI or English
        self.pUnits = "bar"
        self.tUnits = "C"
        self.hUnits = "kJ/kg"
        self.uUnits = "kJ/kg"
        self.sUnits = "kJ/kg*C"
        self.vUnits = "m^3/kg"

        # Initialize with correct unit labels
        self.setUnits()

    def setupSignals(self):
        # Radio buttons
        self.rdoSI.clicked.connect(self.setUnits)
        self.rdoEnglish.clicked.connect(self.setUnits)

        # Property combos
        self.cmbProp1S1.currentIndexChanged.connect(self.setUnits)
        self.cmbProp2S1.currentIndexChanged.connect(self.setUnits)
        self.cmbProp1S2.currentIndexChanged.connect(self.setUnits)
        self.cmbProp2S2.currentIndexChanged.connect(self.setUnits)

        # Calculate button
        self.pbCalculate.clicked.connect(self.calculateProperties)

    @pyqtSlot()
    def setUnits(self):
        """
        Update displayed units for property combos, and if user toggled from
        SI<->English, convert numeric QLineEdit values too.
        """
        SI = self.rdoSI.isChecked()
        newUnits = 'SI' if SI else 'EN'
        unitChange = (newUnits != self.currentUnits)
        self.currentUnits = newUnits

        # Decide labels
        if SI:
            self.pUnits = "bar"
            self.tUnits = "C"
            self.hUnits = "kJ/kg"
            self.uUnits = "kJ/kg"
            self.sUnits = "kJ/kg*C"
            self.vUnits = "m^3/kg"
        else:
            self.pUnits = "psi"
            self.tUnits = "F"
            self.hUnits = "btu/lb"
            self.uUnits = "btu/lb"
            self.sUnits = "btu/lb*F"
            self.vUnits = "ft^3/lb"

        # helper to parse "Pressure (p)" -> "p"
        def shortProp(cmbText):
            if '(' in cmbText and ')' in cmbText:
                return cmbText[cmbText.index('(')+1 : cmbText.index(')')].lower()
            return ""

        # function to do numeric conversions
        def convertValue(val, propType, oldIsSI, newIsSI):
            if oldIsSI == newIsSI:
                return val
            # oldIsSI=True => going from SI->English
            if propType == 'p':
                return val * UC.bar_to_psi if oldIsSI else val * UC.psi_to_bar
            elif propType == 't':
                return UC.C_to_F(val) if oldIsSI else UC.F_to_C(val)
            elif propType in ['h', 'u']:
                return val * UC.kJperkg_to_btuperlb if oldIsSI else val * UC.btuperlb_to_kJperkg
            elif propType == 's':
                return val * UC.kJperkgC_to_btuperlbF if oldIsSI else val * UC.btuperlbF_to_kJperkgC
            elif propType == 'v':
                return val * UC.m3perkg_to_ft3perlb if oldIsSI else val * UC.ft3perlb_to_m3perkg
            elif propType == 'x':
                return val
            return val

        oldIsSI = (not SI)

        # For each property line (S1P1, S1P2, S2P1, S2P2)
        # a small function to handle them in one step
        def updateLineEdit(cmb, leVal, lblUnits):
            propType = shortProp(cmb.currentText())
            val = float(leVal.text())
            if unitChange:
                val = convertValue(val, propType, oldIsSI, SI)

            # set label
            if propType == 'p': lblUnits.setText(self.pUnits)
            elif propType == 't': lblUnits.setText(self.tUnits)
            elif propType == 'h': lblUnits.setText(self.hUnits)
            elif propType == 'u': lblUnits.setText(self.uUnits)
            elif propType == 's': lblUnits.setText(self.sUnits)
            elif propType == 'v': lblUnits.setText(self.vUnits)
            else: lblUnits.setText("")

            leVal.setText(f"{val:.3f}")

        # State 1
        updateLineEdit(self.cmbProp1S1, self.lePropVal1S1, self.lblUnits1S1)
        updateLineEdit(self.cmbProp2S1, self.lePropVal2S1, self.lblUnits2S1)

        # State 2
        updateLineEdit(self.cmbProp1S2, self.lePropVal1S2, self.lblUnits1S2)
        updateLineEdit(self.cmbProp2S2, self.lePropVal2S2, self.lblUnits2S2)

    def makeLabel(self, st):
        """
        Returns a multi-line string describing the given thermodynamic state
        with property names and units, e.g.:
            Region: sub-cooled liquid
            Pressure = 1.000 (bar)
            Temperature = 100.000 (C)
            ...
        """
        lines = []
        lines.append(f"Region: {st.region}")
        lines.append(f"Pressure = {st.p:.3f} ({self.pUnits})")
        lines.append(f"Temperature = {st.t:.3f} ({self.tUnits})")
        lines.append(f"Internal Energy = {st.u:.3f} ({self.uUnits})")
        lines.append(f"Enthalpy = {st.h:.3f} ({self.hUnits})")
        lines.append(f"Entropy = {st.s:.3f} ({self.sUnits})")
        lines.append(f"Specific Volume = {st.v:.5f} ({self.vUnits})")
        lines.append(f"Quality = {st.x:.3f}")
        return "\n".join(lines)

    def makeDeltaLabel(self, s1, s2):
        """
        Returns a multi-line string of differences, e.g.
            ΔPressure = 0.000 (bar)
            ΔTemperature = 100.000 (C)
            ...
        """
        dp = s2.p - s1.p
        dT = s2.t - s1.t
        du = s2.u - s1.u
        dh = s2.h - s1.h
        ds = s2.s - s1.s
        dv = s2.v - s1.v
        dx = s2.x - s1.x

        lines = []
        lines.append(f"ΔPressure = {dp:.3f} ({self.pUnits})")
        lines.append(f"ΔTemperature = {dT:.3f} ({self.tUnits})")
        lines.append(f"ΔInternal Energy = {du:.3f} ({self.uUnits})")
        lines.append(f"ΔEnthalpy = {dh:.3f} ({self.hUnits})")
        lines.append(f"ΔEntropy = {ds:.3f} ({self.sUnits})")
        lines.append(f"ΔSpecific Volume = {dv:.5f} ({self.vUnits})")
        lines.append(f"ΔQuality = {dx:.3f}")
        return "\n".join(lines)

    @pyqtSlot()
    def calculateProperties(self):
        self.lblWarning.setText("")  # clear any old warning

        def shortProp(cmbText):
            if '(' in cmbText and ')' in cmbText:
                return cmbText[cmbText.index('(')+1 : cmbText.index(')')].lower()
            return ""

        # Gather State 1 combos & values
        sp1S1 = shortProp(self.cmbProp1S1.currentText())
        sp2S1 = shortProp(self.cmbProp2S1.currentText())
        val1S1 = float(self.lePropVal1S1.text())
        val2S1 = float(self.lePropVal2S1.text())

        # Gather State 2 combos & values
        sp1S2 = shortProp(self.cmbProp1S2.currentText())
        sp2S2 = shortProp(self.cmbProp2S2.currentText())
        val1S2 = float(self.lePropVal1S2.text())
        val2S2 = float(self.lePropVal2S2.text())

        # Check for same property repeated
        if sp1S1 == sp2S1:
            self.lblWarning.setText("State 1: cannot specify the same property twice.")
            return
        if sp1S2 == sp2S2:
            self.lblWarning.setText("State 2: cannot specify the same property twice.")
            return

        # Create two states
        SI = (self.currentUnits == 'SI')
        s1 = thermoState()
        s2 = thermoState()

        try:
            s1.setState(sp1S1, sp2S1, val1S1, val2S1, SI)
            s2.setState(sp1S2, sp2S2, val1S2, val2S2, SI)

            label1 = self.makeLabel(s1)
            label2 = self.makeLabel(s2)
            labelDelta = self.makeDeltaLabel(s1, s2)

            self.lblResultsS1.setText(label1)
            self.lblResultsS2.setText(label2)
            self.lblResultsDelta.setText(labelDelta)

        except ValueError as ex:
            self.lblWarning.setText(f"Error: {ex}")
        except Exception as ex:
            self.lblWarning.setText(f"Unexpected error: {ex}")


###############################################################################
#   MAIN FUNCTION
###############################################################################
def main():
    app = QApplication(sys.argv)
    win = main_window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()