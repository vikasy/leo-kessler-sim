import numpy as np, kessler_sim as ks
RE, MU = ks.RE, ks.MU
# single derelict, Starlink-class B, start 550 km, no station-keeping, no noise
for alt0,label in [(550,'550km derelict'),(800,'800km derelict')]:
    a = RE + alt0*1e3; e=0.0; B=2.2*25/260.0; dt=5*86400.0
    t=0.0
    while (a*(1-e)-RE) > 200e3 and t < 30*365.25*86400:
        rho = ks.density(a*(1-e)-RE)
        dadt = -rho*B*np.sqrt(MU*a)
        a += dadt*dt; t += dt
    print(f"{label}: B={B:.4f} m2/kg -> decay to 200km in {t/(365.25*86400):.2f} yr")
# also a low-A/m fragment (dense chunk) and high-A/m flake at 550
for am,lab in [(0.005,'dense chunk A/m=0.005'),(0.05,'nominal frag A/m=0.05'),(0.5,'flake A/m=0.5')]:
    a=RE+550e3; e=0.0; B=2.2*am; dt=5*86400.0; t=0.0
    while (a*(1-e)-RE)>200e3 and t<200*365.25*86400:
        rho=ks.density(a*(1-e)-RE); a+= -rho*B*np.sqrt(MU*a)*dt; t+=dt
    print(f"550km {lab}: B={B:.4f} -> {t/(365.25*86400):.2f} yr")
