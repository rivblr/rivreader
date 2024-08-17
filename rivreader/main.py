import tkinter as tk
from src.gui import ModernReadingCompanionGUI

def main():
    try:
        root = tk.Tk()
        app = ModernReadingCompanionGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred while starting the application: {str(e)}")
        # You might want to show a messagebox here to inform the user

if __name__ == "__main__":
    main()