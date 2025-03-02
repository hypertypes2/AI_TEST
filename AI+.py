import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.stats import mode
import warnings

warnings.filterwarnings(action='ignore')

def GetUniqueZone(cases_index, zone):
    zone_dict = {}
    zone_list = []
    for k, v in cases_index.items():
        result = zone.loc[v]
        zone_dict[k] = set(result)
        zone_list.append(mode(result)[0])
    return zone_dict, zone_list


def GetAccuracy(pred, label):
    correct = sum(1 for i in range(len(label)) if pred[i] == label[i])
    return round(correct / len(label), 4)


def ComparePlot(pred, label):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(pred, label='쾌적존', color='b')
    ax.plot(label, label='목표쾌적', alpha=0.5, color='r')
    ax.legend()
    ax.set_yticks([1, 2, 3, 4, 5])
    st.pyplot(fig)


def FindIndex(data, case):
    a = data['설정온도_1'] == case[0]
    b = data['공기_1'] == case[1]
    c = data['습도_1'] == case[2]
    return data[a & b & c].index

st.title("멀티 VS 단일 비교 앱")

tab1, tab2 = st.tabs(["멀티 VS", "멀티 단일"])

with tab1:
    test_path = st.text_input("테스트 데이터 경로")
    source_path = st.text_input("소스 데이터 경로")
    
    if test_path and source_path:
        default_temp = 31.8  # 멀티V S

        Data = pd.read_csv(test_path, encoding="cp949")
        source = pd.read_csv(source_path, encoding="cp949")

        multivs_cool_index = source[source['2TH1'] == default_temp].index
        source_info = source.loc[multivs_cool_index, ['희망온도1', '습도1', '2TH1']]
        test_result = Data.loc[multivs_cool_index, ['쾌적존1', '목표쾌적1']]

        cases = defaultdict(list)
        cases_index = defaultdict(list)
        
        MIN_TEMP, MAX_TEMP = 16, 30
        MIN_HUM, MAX_HUM = 20, 90
        num = 1

        for set_temp in range(MIN_TEMP, MAX_TEMP + 1):
            for hum in range(MIN_HUM, MAX_HUM + 10, 10):
                cases[num] = [default_temp, set_temp, hum]
                num += 1

        for k, v in cases.items():
            a = source_info['2TH1'] == v[0]
            b = source_info['희망온도1'] == v[1]
            c = source_info['습도1'] == v[2]
            cases_index[k] = list(source_info[a & b & c].index)

        pred = GetUniqueZone(cases_index, test_result['쾌적존1'])[1]
        label = GetUniqueZone(cases_index, test_result['목표쾌적1'])[1]

        st.write(f"정확도: {GetAccuracy(pred, label)}")
        ComparePlot(pred, label)

with tab2:
    mv_path = st.text_input("멀티 데이터 경로")
    test_path = st.text_input("테스트 데이터 경로")
    
    if mv_path and test_path:
        default_temp = 31.58  # 멀티

        mv_data = pd.read_csv(mv_path, encoding='utf-8', skiprows=11)
        test_data = pd.read_csv(test_path, encoding='cp949')

        MIN_TEMP, MAX_TEMP = 16, 30
        MIN_HUM, MAX_HUM = 20, 90

        last_case_idx = FindIndex(mv_data, [MAX_TEMP, default_temp, MAX_HUM])
        start_case_idx = FindIndex(mv_data, [MIN_TEMP, default_temp, MIN_HUM])

        start_time = mv_data.loc[start_case_idx[-15], 'Time']
        end_time = mv_data.loc[last_case_idx[-1], 'Time']

        mv_data = mv_data[(mv_data['Time'] >= start_time) & (mv_data['Time'] <= end_time)]
        zone = test_data[(test_data['시간'] >= start_time) & (test_data['시간'] <= end_time)][['시간', '쾌적존1']]

        cases = defaultdict(list)
        cases_times = defaultdict(list)
        pred = []
        num = 1
        
        for set_temp in range(MIN_TEMP, MAX_TEMP + 1):
            for hum in range(MIN_HUM, MAX_HUM + 10, 10):
                cases[num] = [default_temp, set_temp, hum]
                num += 1

        for k, v in cases.items():
            a = mv_data['공기_1'] == v[0]
            b = mv_data['설정온도_1'] == v[1]
            c = mv_data['습도_1'] == v[2]
            times = list(mv_data[a & b & c]['Time'])
            cases_times[k] = times

        for k, v in cases_times.items():
            a = zone['시간'] >= v[0]
            b = zone['시간'] <= v[-1]
            result = zone[a & b]['쾌적존1']
            pred.append(mode(result)[0] if len(result) > 0 else 0)

        label = GetUniqueZone(cases_times, test_data['목표쾌적1'])[1]

        st.write(f"정확도: {GetAccuracy(pred, label)}")
        ComparePlot(pred, label)
