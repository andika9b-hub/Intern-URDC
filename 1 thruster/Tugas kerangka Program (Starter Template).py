
# =====================================================
# SIMULASI PENGENDALIAN 4 THRUSTER ASV
# Python - Object Oriented Programming
# =====================================================


# ===================== CLASS THRUSTER =====================

class Thruster:
    def __init__(self, name):
        self.name = name
        self.output = 0

    def set_output(self, value):
        # Membatasi output antara -100 sampai +100
        self.output = max(-100, min(100, value))

    def stop(self):
        # Menghentikan thruster
        self.output = 0


# ===================== CLASS ASV CONTROLLER =====================

class ASVController:
    def __init__(self):
        # Membuat empat objek thruster
        self.thrusters = {
            "FL": Thruster("FL"),
            "FR": Thruster("FR"),
            "RL": Thruster("RL"),
            "RR": Thruster("RR")
        }

        self.status = "STOP"

    # ===================== GERAK MAJU =====================

    def forward(self, speed):
        for thruster in self.thrusters.values():
            thruster.set_output(speed)

        self.status = "FORWARD"

    # ===================== GERAK MUNDUR =====================

    def backward(self, speed):
        for thruster in self.thrusters.values():
            thruster.set_output(-speed)

        self.status = "BACKWARD"

    # ===================== BELOK KIRI =====================

    def turn_left(self, turn_value=30):
        self.thrusters["FL"].set_output(-turn_value)
        self.thrusters["FR"].set_output(turn_value)
        self.thrusters["RL"].set_output(-turn_value)
        self.thrusters["RR"].set_output(turn_value)

        self.status = "TURN LEFT"

    # ===================== BELOK KANAN =====================

    def turn_right(self, turn_value=30):
        self.thrusters["FL"].set_output(turn_value)
        self.thrusters["FR"].set_output(-turn_value)
        self.thrusters["RL"].set_output(turn_value)
        self.thrusters["RR"].set_output(-turn_value)

        self.status = "TURN RIGHT"

    # ===================== STOP =====================

    def stop(self):
        for thruster in self.thrusters.values():
            thruster.stop()

        self.status = "STOP"

    # ===================== EMERGENCY STOP =====================

    def emergency_stop(self):
        for thruster in self.thrusters.values():
            thruster.stop()

        self.status = "EMERGENCY STOP"

    # ===================== DISPLAY STATUS =====================

    def display_status(self):
        print("\n========== STATUS KAPAL ==========")
        print(f"Gerakan Kapal : {self.status}")

        for name, thruster in self.thrusters.items():
            print(f"{name} : {thruster.output:+d}")

        print("==================================\n")


# ===================== VALIDASI INPUT =====================

def input_speed():
    try:
        speed = int(input("Masukkan kecepatan (0-100): "))

        if speed < 0 or speed > 100:
            print("ERROR: Kecepatan harus antara 0 sampai 100!")
            return None

        return speed

    except ValueError:
        print("ERROR: Input harus berupa angka!")
        return None


# ===================== PROGRAM UTAMA =====================

def main():
    asv = ASVController()

    while True:
        print("\n================================")
        print("      ASV THRUSTER CONTROL")
        print("================================")
        print("1. Forward")
        print("2. Backward")
        print("3. Turn Left")
        print("4. Turn Right")
        print("5. Stop")
        print("6. Emergency Stop")
        print("7. Exit")
        print("================================")

        choice = input("Pilih perintah (1-7): ")

        if choice == "1":
            speed = input_speed()

            if speed is not None:
                asv.forward(speed)
                asv.display_status()

        elif choice == "2":
            speed = input_speed()

            if speed is not None:
                asv.backward(speed)
                asv.display_status()

        elif choice == "3":
            asv.turn_left()
            asv.display_status()

        elif choice == "4":
            asv.turn_right()
            asv.display_status()

        elif choice == "5":
            asv.stop()
            asv.display_status()

        elif choice == "6":
            asv.emergency_stop()
            asv.display_status()

        elif choice == "7":
            asv.stop()
            print("Program dihentikan. Semua thruster OFF.")
            break

        else:
            print("Pilihan tidak valid! Silakan pilih 1-7.")


# ===================== MENJALANKAN PROGRAM =====================

if __name__ == "__main__":
    main()
