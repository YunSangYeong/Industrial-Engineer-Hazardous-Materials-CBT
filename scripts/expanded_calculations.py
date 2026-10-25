"""Forty explicitly labelled calculation contexts, twenty conditions each.

All values are textbook assumptions, not measured material properties, legal
thresholds, equipment instructions or field safety/design recommendations.
"""
from decimal import Decimal as D, ROUND_HALF_UP


def expand(numeric, subjects):
    def f(v):
        return format(D(str(v)).normalize(), 'f')

    def emit(subject, kind, topic, text, values, answer, unit, formula, substitution, note=""):
        raw = D(str(answer))
        result = raw.quantize(D('0.001'), rounding=ROUND_HALF_UP)
        rounding = "계산값은 필요한 경우 소수 넷째 자리에서 반올림하여 셋째 자리까지 표시한다."
        explanation = (f"조건: {text} 적용식: {formula}. 대입: {substitution}. "
            f"결과는 {f(result)} {unit}이다. {rounding} {note}")
        numeric(subject, topic, kind, 0, text + " " + rounding,
            [float(v) for v in values], result, unit, explanation)

    for i in range(1, 21):
        # General chemistry: 14 contexts.
        s = subjects[0]
        emit(s, 'mass-percent', '질량 백분율 계산',
            f"용액 200 g에 용질 {2*i} g이 들어 있다. 질량 백분율 농도는?",
            [2*i,200], i, '%', 'w=용질 질량/용액 질량×100', f'{2*i} g/200 g×100={i} %',
            '분모는 용매가 아니라 최종 용액 질량이다.')
        n = D(i)/10
        emit(s, 'molality', '몰랄 농도 계산',
            f"용매 500 g에 용질 {f(n)} mol이 녹아 있다. 몰랄 농도는?",
            [n,500], n/D('.5'), 'mol/kg', 'b=n/용매 질량(kg)', f'500 g=0.5 kg, {f(n)} mol/0.5 kg',
            '몰 농도는 용액 부피 기준이지만 몰랄 농도는 용매 질량 기준이다.')
        c = i+1
        emit(s, 'dilution-volume', '희석 후 최종 부피',
            f"{c} mol/L 용액 50 mL를 반응·손실 없이 0.5 mol/L로 희석한다. 최종 용액 부피는?",
            [c,50,D('.5')], c*100, 'mL', 'C₁V₁=C₂V₂', f'V₂={c}×50/0.5 mL',
            '양쪽 농도 단위가 같으므로 부피는 mL로 계산할 수 있다. 추가할 물이 아닌 최종 부피를 묻는다.')
        emit(s, 'ideal-volume', '이상기체 상태식',
            f"300 K, 절대압력 100 kPa에서 이상기체 {i} mol의 부피는? R=8.314 kPa·L/(mol·K)로 둔다.",
            [i,300,100,D('8.314')], D(i)*300*D('8.314')/100, 'L', 'V=nRT/P', f'{i} mol×8.314 kPa·L/(mol·K)×300 K/100 kPa',
            '이상기체 가정이며 단위가 약분되어 L가 된다.')
        p = 100+5*i
        emit(s, 'boyle-pressure', '등온 압축',
            f"일정량의 이상기체를 일정 온도에서 2 L에서 1 L로 압축한다. 처음 절대압력이 {p} kPa일 때 나중 절대압력은?",
            [p,2,1], 2*p, 'kPa', 'P₁V₁=P₂V₂', f'P₂={p} kPa×2 L/1 L', '절대압력을 사용하며 기체 누출은 없다.')
        t = 300+10*i
        emit(s, 'charles-volume', '등압 기체 팽창',
            f"일정량의 이상기체가 일정 압력에서 300 K일 때 3 L이다. {t} K에서의 부피는?",
            [3,300,t], D(3)*t/300, 'L', 'V₁/T₁=V₂/T₂', f'V₂=3 L×{t} K/300 K', '온도는 켈빈을 사용한다.')
        x = 10+i
        emit(s, 'partial-pressure', '기체 분압',
            f"이상기체 혼합물의 전체 절대압력은 200 kPa이다. 몰분율 {x}%인 성분의 분압은?",
            [200,x], 2*x, 'kPa', 'P성분=몰분율×P전체', f'{x}/100×200 kPa', '달톤 분압 법칙을 적용하는 이상 혼합물이다.')
        m = 24+12*i
        emit(s, 'gas-density', '몰부피와 기체 밀도',
            f"주어진 조건에서 기체의 몰부피는 24 L/mol, 몰질량은 {m} g/mol이다. 밀도는?",
            [m,24], D(m)/24, 'g/L', 'ρ=M/V몰', f'{m} g/mol÷24 L/mol', '몰부피는 문제에서 제공한 가정이며 실제 특정 기체의 측정값이 아니다.')
        actual = 50+i
        emit(s, 'reaction-yield', '반응 수율',
            f"반응식으로 계산한 이론 생성량이 100 g이고 순수 생성물의 실제 회수량이 {actual} g이다. 수율은?",
            [actual,100], actual, '%', '수율=실제 생성량/이론 생성량×100', f'{actual} g/100 g×100', '회수물은 순수하며 부반응 생성물을 포함하지 않는 조건이다.')
        ca = D('.1') + D(i)/100
        emit(s, 'neutralization-volume', '중화의 몰수 비',
            f"1가 산 {f(ca)} mol/L 용액 20 mL를 1:1 몰비로 중화할 때 필요한 0.1 mol/L 1가 염기 용액의 부피는?",
            [ca,20,D('.1')], ca*200, 'mL', 'C산V산=C염기V염기', f'{f(ca)}×20/0.1 mL', '반응식의 산과 염기의 몰비가 1:1이며 실험 취급 절차가 아닌 양론 계산이다.')
        x = i+10
        avg = (D(20)*x+D(40)*(100-x))/100
        emit(s, 'mixture-molar-mass', '혼합기체 평균 몰질량',
            f"이상 혼합기체에서 몰질량 20 g/mol인 A의 몰분율은 {x}%, 몰질량 40 g/mol인 B는 나머지이다. 평균 몰질량은?",
            [20,40,x], avg, 'g/mol', 'M평균=x_A M_A+x_B M_B', f'20×{x}/100+40×{100-x}/100 g/mol', '몰분율로 가중 평균하며 질량분율과 혼동하지 않는다.')
        water = 50+5*i
        emit(s, 'solubility-mass', '용해도와 용질 질량',
            f"어떤 온도에서 물 100 g당 용질 20 g이 녹는다고 가정한다. 같은 온도에서 물 {water} g에 포화될 때 녹는 용질 질량은?",
            [20,100,water], D(water)/5, 'g', '용질 질량=용해도×물 질량/기준 물 질량', f'20 g×{water} g/100 g', '용해도는 가상으로 주어진 값이며 특정 물질의 공식 물성이 아니다.')
        pct = i+20
        average = (D(10)*pct+D(11)*(100-pct))/100
        emit(s, 'isotope-mass', '동위원소 평균 질량',
            f"동위원소 질량을 각각 정확히 10 u, 11 u로 가정한다. 존재 비율이 각각 {pct}%, {100-pct}%일 때 원자 1개의 평균 질량은?",
            [10,11,pct], average, 'u', '평균 질량=Σ(동위원소 질량×존재비)', f'10×{pct}/100+11×{100-pct}/100 u', '실제 특정 원소의 질량값이 아니라 주어진 두 동위원소의 가중 평균 연습이다.')
        n = D(i)/100
        emit(s, 'faraday-charge', '전자 몰수와 전하량',
            f"전자 {f(n)} mol이 이동할 때 전하량의 크기는? 패러데이 상수 F=96485 C/mol로 둔다.",
            [n,96485], n*96485, 'C', '전하량의 크기 Q=nF', f'{f(n)} mol×96485 C/mol', '전자 전하의 부호가 아닌 전하량 크기를 묻는다.')

        # Fire prevention / extinguishing principles: 13 contexts.
        s = subjects[1]
        mass = i*10
        emit(s, 'latent-heat', '물의 기화 냉각',
            f"이미 끓는점에 도달한 물 {mass} g이 모두 기화한다. 기화열을 2256 J/g로 가정할 때 기화에 흡수되는 열은?",
            [mass,2256], mass*2256, 'J', 'Q=mL', f'{mass} g×2256 J/g', '끓는점까지 올리는 현열과 외부 열손실은 계산하지 않는다.')
        heat = 420*(i+1)
        emit(s, 'temperature-rise', '물 냉각 시 온도 변화',
            f"물 100 g이 {heat} J을 흡수한다. 비열은 4.2 J/(g·K), 상태 변화·열손실은 없을 때 온도 상승 폭은?",
            [heat,100,D('4.2')], i+1, 'K', 'ΔT=Q/(mc)', f'{heat} J/(100 g×4.2 J/(g·K))', '최종 절대온도가 아닌 온도 차를 구한다.')
        energy = 60*(i+1)
        emit(s, 'heat-release-rate', '평균 열방출률',
            f"모형 화재에서 60초 동안 {energy} kJ의 열이 방출되었다. 평균 열방출률은?",
            [energy,60], i+1, 'kW', '평균 열방출률=열에너지/시간', f'{energy} kJ/60 s', '1 kJ/s=1 kW이며 순간 최대 열방출률과 다르다.')
        mass = D(i)/2
        emit(s, 'combustion-energy', '연소 에너지',
            f"가상 연료의 유효 발열량을 20000 kJ/kg로 둔다. {f(mass)} kg이 주어진 발열량대로 연소할 때 총 열에너지는?",
            [mass,20000], mass*20000, 'kJ', 'Q=mH', f'{f(mass)} kg×20000 kJ/kg', '가상의 발열량과 완전한 에너지 환산 조건이며 실제 연소시험값이 아니다.')
        energy = 500*(i+1)
        emit(s, 'fire-load-density', '면적당 화재 하중',
            f"바닥 면적 100 m²의 모형 공간에 가연물의 총 잠재 연소에너지가 {energy} MJ이다. 단위 바닥 면적당 에너지는?",
            [energy,100], 5*(i+1), 'MJ/m²', '면적당 에너지=총 에너지/바닥 면적', f'{energy} MJ/100 m²', '법정 시설 기준 판정이나 실제 화재 성장 속도 예측은 아니다.')
        power = 5*i
        emit(s, 'heat-flux', '열유속',
            f"2 m²의 표면에 균일하게 {power} kW의 열이 전달된다. 평균 열유속은?",
            [power,2], D(power)/2, 'kW/m²', '열유속=전달 열량률/면적', f'{power} kW/2 m²', '균일 분포 가정의 평균값이며 노출 안전 한계 수치가 아니다.')
        dt = 20+2*i
        emit(s, 'conduction-rate', '평판 열전도',
            f"두께 0.1 m, 면적 2 m²인 평판의 양면 온도 차가 {dt} K이다. 열전도율은 0.5 W/(m·K), 정상 1차원 전도만 고려할 때 열전달률은?",
            [D('.5'),2,dt,D('.1')], 10*dt, 'W', '열전달률=kAΔT/두께', f'0.5 W/(m·K)×2 m²×{dt} K/0.1 m', '평판 내부 열전도만 계산하며 대류·복사와 접촉 저항은 제외한다.')
        dt = 5+i
        emit(s, 'convection-rate', '대류 열전달',
            f"면적 2 m² 표면과 유체의 온도 차가 {dt} K이다. 대류 열전달계수 10 W/(m²·K)를 가정할 때 대류 열전달률의 크기는?",
            [10,2,dt], 20*dt, 'W', '열전달률=hAΔT', f'10 W/(m²·K)×2 m²×{dt} K', '가정한 일정 계수의 대류만 계산하며 실제 화재 계수의 측정값이 아니다.')
        volume = 300+20*i
        emit(s, 'water-duration', '유량과 공급 시간',
            f"모형 수조에 물 {volume} L가 있고 일정 유량 20 L/min으로 공급한다. 잔량과 추가 유입을 무시하면 공급 가능한 시간은?",
            [volume,20], D(volume)/20, 'min', '시간=저장 부피/체적 유량', f'{volume} L/(20 L/min)', '설비의 법정 방사 시간이나 실제 펌프 성능 판정은 아니다.')
        liquid = 10+i
        emit(s, 'foam-volume', '포 팽창비',
            f"모형 시험에서 포 팽창비를 생성된 포 부피/혼합액 부피=20으로 둔다. 혼합액 {liquid} L에서 만들어지는 포 부피는?",
            [liquid,20], 20*liquid, 'L', 'V포=팽창비×V혼합액', f'20×{liquid} L', '가상의 팽창비이며 제품별 성능이나 현장 약제 배합 지침은 아니다.')
        foam = 200+20*i
        emit(s, 'foam-liquid-required', '포 부피 역산',
            f"포 팽창비가 20인 가상 모형에서 포 {foam} L에 해당하는 혼합액 부피는? 팽창비=포 부피/혼합액 부피로 정의한다.",
            [foam,20], D(foam)/20, 'L', 'V혼합액=V포/팽창비', f'{foam} L/20', '산술 역산이며 원액 농도 또는 실제 방출량을 정하는 지침이 아니다.')
        area = 10+i
        emit(s, 'water-layer-volume', '면적과 물의 부피',
            f"모형 표면 {area} m²에 물을 균일한 깊이 10 mm로 채운다. 물의 부피는?",
            [area,10], area*10, 'L', 'V=면적×깊이', f'10 mm=0.01 m, {area}×0.01 m³×1000 L/m³', '유출·흡수는 없으며 실제 소화에 필요한 물의 양이라는 뜻은 아니다.')
        useful = 500+10*i
        emit(s, 'heat-use-efficiency', '유효 흡열 비율',
            f"모형 열원에서 나온 열 1000 kJ 중 물이 흡수한 열은 {useful} kJ이다. 전체 열 중 물이 흡수한 비율은?",
            [useful,1000], D(useful)/10, '%', '비율=유효 흡열량/전체 열량×100', f'{useful} kJ/1000 kJ×100', '주어진 에너지 수지의 비율이며 특정 소화 시스템의 실제 효율이 아니다.')

        # Properties / handling: 13 physical inventory and measurement contexts.
        s = subjects[2]
        volume = 100+10*i
        emit(s, 'liquid-mass', '밀도와 저장 질량',
            f"가상 액체의 밀도가 0.8 kg/L이고 부피가 {volume} L이다. 질량은?",
            [D('.8'),volume], D('.8')*volume, 'kg', 'm=ρV', f'0.8 kg/L×{volume} L', '밀도는 문제의 가정이며 실제 물질의 온도별 물성과 구별한다.')
        mass = 50+5*i
        emit(s, 'liquid-volume', '질량으로 부피 계산',
            f"밀도 1.25 kg/L인 가상 액체 {mass} kg의 부피는?",
            [mass,D('1.25')], D(mass)/D('1.25'), 'L', 'V=m/ρ', f'{mass} kg/(1.25 kg/L)', '주어진 일정 밀도를 사용하며 질량과 부피 단위를 맞춘다.')
        emit(s, 'thermal-volume-increase', '액체 부피 팽창',
            f"가상 액체의 처음 부피는 100 L, 일정 체적팽창계수는 0.001/K이다. 온도 차 {i} K 상승에 따른 선형 근사 부피 증가량은?",
            [100,D('.001'),i], D(i)/10, 'L', 'ΔV=βV₀ΔT', f'0.001/K×100 L×{i} K', '선형 근사 증가량이며 최종 부피나 실제 용기 충전 한계가 아니다.')
        depth = D('.1')+D(i)/100
        emit(s, 'rectangular-volume', '직육면체 집수 부피',
            f"가로 2 m, 세로 1 m인 빈 직육면체 모형에 액체가 {f(depth)} m 높이까지 찼다. 그 액체 부피는?",
            [2,1,depth], 2*depth*1000, 'L', 'V=가로×세로×깊이', f'2 m×1 m×{f(depth)} m×1000 L/m³', '내부 구조물과 기울기를 무시한 기하학 계산으로 법적 집수시설 기준이 아니다.')
        height = D(i)/10
        emit(s, 'cylinder-volume', '원기둥 액체 부피',
            f"내부 반지름 0.5 m인 수직 원기둥 모형에서 액체 깊이는 {f(height)} m이다. π=3.14로 둘 때 액체 부피는?",
            [D('.5'),height,D('3.14')], D('3.14')*D('.25')*height*1000, 'L', 'V=πr²h', f'3.14×(0.5 m)²×{f(height)} m×1000 L/m³', '빈 공간의 기하학 계산이며 실제 탱크의 형상 보정이나 법정 충전 기준은 아니다.')
        volume = 100+5*i
        emit(s, 'fill-percentage', '용기 충전 비율 계산',
            f"모형 용기의 내부 부피는 200 L이며 액체가 {volume} L 들어 있다. 부피 기준 충전 비율은?",
            [volume,200], D(volume)/2, '%', '충전율=액체 부피/내부 부피×100', f'{volume} L/200 L×100', '현재 비율의 산술 계산이며 실제 허용 충전율이나 안전 여부를 제시하지 않는다.')
        volume = 100+10*i
        emit(s, 'headspace-volume', '용기 빈 공간',
            f"내부 부피 500 L의 모형 용기에 액체 {volume} L가 있다. 액체 외 빈 공간 부피는?",
            [500,volume], 500-volume, 'L', '빈 공간=전체 내부 부피−액체 부피', f'500 L−{volume} L', '내부 구조물이 없다는 조건이며 빈 공간만으로 압력 안전성을 판정할 수 없다.')
        milligrams = 10+i
        emit(s, 'mass-trace-concentration', '미량 성분 질량 농도',
            f"모의 혼합물 전체 질량 2 kg에 특정 성분 {milligrams} mg이 들어 있다. mg/kg 단위의 질량 농도는?",
            [milligrams,2], D(milligrams)/2, 'mg/kg', '질량 농도=성분 mg/혼합물 kg', f'{milligrams} mg/2 kg', '노출 기준이나 유해성 한계가 아니라 질량비 환산이다.')
        emit(s, 'mixed-mass-percent', '두 용액의 질량 농도',
            f"동일 용질의 {i} 질량% 용액 10 kg과 20 질량% 용액 10 kg을 반응·손실 없이 섞는다. 최종 질량% 농도는?",
            [i,10,20,10], (D(i)+20)/2, '%', 'w=(각 용질 질량 합)/(용액 질량 합)×100', f'(10×{i}/100+10×20/100)/(10+10)×100', '서로 적합하고 반응하지 않는 모형 용액이며 실제 위험물 혼합을 권고하지 않는다.')
        removed = 10+i
        answer = D(20)/(100-removed)*100
        emit(s, 'evaporation-concentration', '용매 손실 후 질량 농도',
            f"용질 20 kg을 포함한 용액 100 kg에서 순수 용매 {removed} kg만 제거되었다. 용질의 손실·반응이 없을 때 남은 용액의 질량% 농도는?",
            [20,100,removed], answer, '%', 'w=보존 용질 질량/(처음 용액 질량−제거 용매 질량)×100', f'20/(100−{removed})×100 %', '용질은 비휘발성으로 가정한 물질수지이며 실제 용매 증발 작업 지시가 아니다.')
        recovered = 50+i
        emit(s, 'recovery-percentage', '누출액 회수 비율',
            f"모의 누출액 100 L 중 {recovered} L를 회수했다. 처음 누출 부피 기준 회수 비율은?",
            [recovered,100], recovered, '%', '회수율=회수 부피/처음 누출 부피×100', f'{recovered} L/100 L×100', '증발·반응·부피 변화는 없으며 회수율만으로 잔류 위험을 판단하지 않는다.')
        density = D('.7')+D(i)/100
        emit(s, 'density-unit-conversion', '밀도 단위 환산',
            f"가상 시료의 밀도가 {f(density)} g/cm³이다. kg/m³ 단위로 환산하면?",
            [density], density*1000, 'kg/m³', '1 g/cm³=1000 kg/m³', f'{f(density)}×(0.001 kg)/(0.000001 m³)', '질량과 부피의 단위 변환을 함께 적용한다.')
        percent = D(i+1)/1000
        emit(s, 'volume-ppm', '체적 농도 환산',
            f"모형 교정 가스의 체적 농도가 {f(percent)}%이다. 같은 체적 기준 ppm으로 바꾸면?",
            [percent], percent*10000, 'ppm', '1%=10000 ppm(같은 체적 기준)', f'{f(percent)}/100×1000000 ppm', '질량 ppm과 혼동하지 않으며 노출 한계 또는 연소 한계를 제시하는 값이 아니다.')
