# 관련 논문 목록 (EMS 기반 충돌·반동·무게감 햅틱)

## 1. 직접 선행연구 (충돌 반동, 벽, 무게감)
- Lopes, Ion, Baudisch. **Impacto: Simulating Physical Impact by Combining Tactile Stimulation with Electrical Muscle Stimulation.** UIST 2015. https://plopes.org/wp-content/uploads/papers/2015-UIST-Impacto.pdf
- Lopes, You, Cheng, Marwecki, Baudisch. **Providing Haptics to Walls & Heavy Objects in Virtual Reality by Means of Electrical Muscle Stimulation.** CHI 2017. https://dl.acm.org/doi/10.1145/3025453.3025600 (프로젝트 페이지: http://plopes.org/project/haptics-vr-walls-objects-using-ems/)
- Lopes, Baudisch. **Muscle-Propelled Force Feedback: Bringing Force Feedback to Mobile Devices.** CHI 2013.
- **Give Weight to VR: Manipulating Users' Perception of Weight in Virtual Reality with Electric Muscle Stimulation.** Mensch und Computer 2022. https://dl.acm.org/doi/fullHtml/10.1145/3543758.3547571
- **Haptic feedback for interactive AR/VR systems: comparing single- vs. dual-muscle EMS for weight perception.** Virtual Reality (Springer), 2025. https://link.springer.com/article/10.1007/s10055-025-01204-2
- **Experiencing Dynamic Weight Changes in VR Through Pseudo-Haptics and Vibrotactile Feedback.** CHI 2024. https://dl.acm.org/doi/10.1145/3613904.3642552 (EMS + C/D ratio 결합으로 무게 범위 2배 언급)
- **Evaluation of Electric Muscle Stimulation Method for Haptic Augmented Reality.** Sensors 2023. https://doi.org/10.3390/s23041796

## 2. 하드웨어 / 툴킷
- Lopes 외. **openEMSstim: open-hardware module to adjust the intensity of EMS/TENS stimulators.** https://github.com/PedroLopes/openEMSstim
  - 파라미터 튜토리얼: https://github.com/PedroLopes/openEMSstim/blob/master/start-here-tutorials/4.exploring_ems_settings_and_parameters.md
  - 하지 말아야 할 것: https://github.com/PedroLopes/openEMSstim/blob/master/start-here-tutorials/0.WhatNotToDo.md
- Lopes. **Interactive Systems based on Electrical Muscle Stimulation.** SIGGRAPH 2017 Labs. https://history.siggraph.org/wp-content/uploads/2022/06/2017-Labs-Lopes_Interactive-Systems.pdf
- HPI Baudisch Lab EMS 프로젝트 페이지: https://hpi.de/baudisch/projects/ems.html

## 3. 서베이 / 리뷰
- **A Comprehensive Survey of Electrical Stimulation Haptic Feedback in Human-Computer Interaction.** arXiv 2025 (110편 체계적 리뷰). https://arxiv.org/abs/2504.21477
- Faltaous 외. **From Perception to Action: A Review and Taxonomy on Electrical Muscle Stimulation in HCI.** 2023. https://www.researchgate.net/publication/366678214

## 4. 기초 / 초기 연구
- Tamaki, Miyaki, Rekimoto. **PossessedHand: Techniques for Controlling Human Hands using Electrical Muscles Stimuli.** CHI 2011. https://lab.rekimoto.org/projects/possessedhand/
- Kruijff, Schmalstieg, Beckhaus. **Using Neuromuscular Electrical Stimulation for Pseudo-Haptic Feedback.** VRST 2006.

## 5. 지연 · 주체감 · 수용성
- Kasahara, Nishida, Lopes. **Preemptive Action: Accelerating Human Reaction using EMS Without Compromising Agency.** CHI 2019. https://lab.plopes.org/published/2019-CHI-AgencyEMS.pdf
- Knibbe, Alsmith, Hornbæk. **Experiencing Electrical Muscle Stimulation.** IMWUT 2018. https://dl.acm.org/doi/10.1145/3264928
- **Would Users Accept Electric Muscle Stimulation Controlling their Body?** CHI EA 2022. https://dl.acm.org/doi/abs/10.1145/3491101.3519693
- Lopes. **EMS in HCI: 10 years later... what about the question of agency?** ACM CHI Medium. https://medium.com/acm-chi/electrical-muscle-stimulation-in-hci-10-years-later-what-about-the-question-of-agency-34516f0b05e2

## 슬라이드 인용 요령
- 컨셉 근거: Impacto(충돌 반동), Walls & Heavy Objects(벽·무게감, 삼두근 길항 자극, 시각 클램핑).
- 기기 선택 근거: openEMSstim README(상용 TENS/EMS 70~100mA급 권장, 출력단 무개조).
- 무게감 설계 근거: Give Weight to VR, dual-muscle EMS weight perception, CHI 2024 pseudo-haptics 결합.
- 안전·윤리·한계: Knibbe 2018, CHI EA 2022 수용성, Preemptive Action(지연 80ms, 주체감).
- 관련연구 개괄: 2025 arXiv 서베이 한 편으로 110편 커버.
