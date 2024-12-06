import tkinter as tk
from tkinter import ttk, messagebox


# محاسبه فشار بخار اشباع
def saturated_vapor_pressure(temp_c):
    return 0.6108 * (10 ** (7.5 * temp_c / (237.3 + temp_c)))


# محاسبه رطوبت مطلق از رطوبت نسبی
def relative_humidity_to_specific_humidity(relative_humidity, temp_c):
    p_sat = saturated_vapor_pressure(temp_c)
    p_vapor = (relative_humidity / 100) * p_sat
    specific_humidity = 0.622 * p_vapor / (101.325 - p_vapor)  # kg/kg
    return specific_humidity * 1000  # g/kg


# محاسبه راندمان سیستم
def calculate_efficiency():
    try:
        # دریافت داده‌های ورودی
        airflow = float(entry_airflow.get())
        temp_in = float(temp_in_var.get())
        temp_out = float(temp_out_var.get())
        rh_in = float(entry_rh_in.get())
        rh_out = float(entry_rh_out.get())
        power_input = float(entry_power.get())

        # بررسی واحد جریان هوا
        if airflow_unit.get() == "CFM":
            airflow *= 1.699  # تبدیل CFM به m³/h
        if power_unit.get() == "BTU/h":
            power_input /= 3.412  # تبدیل BTU/h به W

        # ثابت‌ها
        air_density = 1.2  # kg/m³
        specific_heat = 1.005  # kJ/(kg·°C)
        latent_heat = 2500  # kJ/kg

        # محاسبه جریان جرمی
        mass_flow_rate = (airflow / 3600) * air_density  # kg/s

        # محاسبه اختلاف دما
        delta_t = temp_in - temp_out

        # محاسبه رطوبت مطلق
        humidity_in = relative_humidity_to_specific_humidity(rh_in, temp_in)
        humidity_out = relative_humidity_to_specific_humidity(rh_out, temp_out)

        # ظرفیت محسوس و نهان
        q_sensible = mass_flow_rate * specific_heat * delta_t * 1000  # W
        delta_humidity = (humidity_in - humidity_out) / 1000  # تبدیل g/kg به kg/kg
        q_latent = mass_flow_rate * latent_heat * delta_humidity * 1000  # W

        # ظرفیت کل
        total_capacity = q_sensible + q_latent

        # محاسبه راندمان‌ها
        cop = total_capacity / power_input
        eer = cop * 3.412

        # نمایش نتایج
        result_text.set(
            f"ظرفیت محسوس: {q_sensible:.2f} W\n"
            f"ظرفیت نهان: {q_latent:.2f} W\n"
            f"ظرفیت کل: {total_capacity:.2f} W\n"
            f"راندمان (COP): {cop:.2f}\n"
            f"راندمان انرژی (EER): {eer:.2f}"
        )
        return airflow, mass_flow_rate, delta_t, q_sensible, q_latent, total_capacity, cop

    except ValueError:
        messagebox.showerror("خطا", "لطفاً مقادیر عددی معتبر وارد کنید.")
        return None


# نمایش محاسبات دستی
def show_manual_calculations():
    result = calculate_efficiency()
    if result is None:
        return

    airflow, mass_flow_rate, delta_t, q_sensible, q_latent, total_capacity, cop = result

    # نمایش محاسبات به تفصیل
    calculation_details = (
        f"1. جریان جرمی:\n"
        f"   Mass Flow Rate = (Airflow / 3600) × Density\n"
        f"   Mass Flow Rate = ({airflow:.2f} / 3600) × 1.2 = {mass_flow_rate:.4f} kg/s\n\n"
        f"2. ظرفیت محسوس:\n"
        f"   Q_sensible = Mass Flow Rate × C_p × ΔT\n"
        f"   Q_sensible = {mass_flow_rate:.4f} × 1.005 × {delta_t:.2f} = {q_sensible:.2f} W\n\n"
        f"3. ظرفیت نهان:\n"
        f"   Q_latent = Mass Flow Rate × h_fg × ΔW\n"
        f"   Q_latent = {q_latent:.2f} W\n\n"
        f"4. ظرفیت کل:\n"
        f"   Q_total = Q_sensible + Q_latent\n"
        f"   Q_total = {total_capacity:.2f} W\n\n"
        f"5. راندمان (COP):\n"
        f"   COP = Q_total / Power_input\n"
        f"   COP = {cop:.2f}\n"
    )

    details_window = tk.Toplevel(root)
    details_window.title("محاسبات دستی")
    details_window.geometry("600x400")
    tk.Label(
        details_window, text=calculation_details, font=("Arial", 12), justify="left", wraplength=580
    ).pack(padx=20, pady=20)


# تغییر دمای ورودی/خروجی
def change_temperature(var, increment):
    current_value = int(var.get())
    var.set(current_value + increment)


# رابط کاربری
root = tk.Tk()
root.title("محاسبه راندمان سیستم تهویه مطبوع")
root.geometry("800x700")
root.configure(bg="#2c3e50")

# متغیرها
result_text = tk.StringVar()
temp_in_var = tk.StringVar(value="25")
temp_out_var = tk.StringVar(value="20")

# ویجت‌ها
ttk.Label(root, text="میزان جریان هوا:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_airflow = ttk.Entry(root)
entry_airflow.grid(row=0, column=1, padx=10, pady=5)
airflow_unit = tk.StringVar(value="m³/h")
ttk.OptionMenu(root, airflow_unit, "m³/h", "CFM").grid(row=0, column=2, padx=5, pady=5)

ttk.Label(root, text="دمای ورودی (°C):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
tk.Button(root, text="-", command=lambda: change_temperature(temp_in_var, -1)).grid(row=1, column=1, sticky="e")
tk.Label(root, textvariable=temp_in_var).grid(row=1, column=2)
tk.Button(root, text="+", command=lambda: change_temperature(temp_in_var, 1)).grid(row=1, column=3, sticky="w")

ttk.Label(root, text="دمای خروجی (°C):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
tk.Button(root, text="-", command=lambda: change_temperature(temp_out_var, -1)).grid(row=2, column=1, sticky="e")
tk.Label(root, textvariable=temp_out_var).grid(row=2, column=2)
tk.Button(root, text="+", command=lambda: change_temperature(temp_out_var, 1)).grid(row=2, column=3, sticky="w")

ttk.Label(root, text="رطوبت نسبی ورودی (%):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_rh_in = ttk.Entry(root)
entry_rh_in.grid(row=3, column=1, padx=10, pady=5)

ttk.Label(root, text="رطوبت نسبی خروجی (%):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_rh_out = ttk.Entry(root)
entry_rh_out.grid(row=4, column=1, padx=10, pady=5)

ttk.Label(root, text="توان مصرفی:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_power = ttk.Entry(root)
entry_power.grid(row=5, column=1, padx=10, pady=5)
power_unit = tk.StringVar(value="W")
ttk.OptionMenu(root, power_unit, "W", "BTU/h").grid(row=5, column=2, padx=5, pady=5)

# دکمه‌ها
ttk.Button(root, text="محاسبه", command=calculate_efficiency).grid(row=6, column=1, pady=20)
ttk.Button(root, text="نمایش محاسبات دستی", command=show_manual_calculations).grid(row=7, column=1, pady=10)

ttk.Label(root, textvariable=result_text, font=("Arial", 14, "bold"), wraplength=700, foreground="white", background="#2c3e50").grid(row=8, column=0, columnspan=3)

root.mainloop()