# -*- coding: utf-8 -*-
"""
cv_source_data.py — 谷英典先生の正式業績データ（一次ソース）

出典：hidenoritani.com「研究業績」ページ（先生提供・2026-07-20）。
ORCID/Crossref より完全かつ正確。CV・業績ページの一次ソースとして使用する。
* = corresponding author, # = equal contribution（原文の表記を保持）。
"""

# --- 原著論文 Original Articles（新しい順・n は原文番号） ---
ORIGINALS = [
    (49, 2026, "Tani H*.", "RNA-binding protein occupancy composition predicts long noncoding RNA subcellular localization.", "Int J Mol Sci 27, 5593", False),
    (48, 2025, "Kurokawa Y, Honda T, Fujii S, Narisawa Y, Ogawa H, Kawashima H, Tani H*.", "Differential regulation of long noncoding RNAs by endogenous and exogenous reactive oxygen species-generating prooxidants in NIH3T3 cells.", "PLoS One 20, e0333072", False),
    (47, 2025, "Endo R, Kurisu M, Tani H*.", "Long noncoding RNA IDI2-AS1 modulates the expression of interleukin 5 in human cells.", "Biochem Biophys Res Commun 761, 151733", False),
    (46, 2024, "Yokoyama S#, Muto H#, Honda T, Kurokawa Y, Ogawa H, Nakajima R, Kawashima H, Tani H*.", "Identification of two long noncoding RNAs, Kcnq1ot1 and Rmst, as biomarkers in chronic liver diseases in mice.", "Int J Mol Sci 25, 8927", False),
    (45, 2024, "Yagi Y, Abe R, Tani H*.", "Exploring IDI2-AS1, OIP5-AS1, and LITATS1: changes in long non-coding RNAs induced by the poly I:C stimulation.", "Biol Pharm Bull 47, 1144-1148", False),
    (44, 2023, "Abe R, Yagi Y, Tani H*.", "Identifying long non-coding RNA as potential indicators of bacterial stress in human cells.", "BPB Reports 6, 226-228", False),
    (43, 2021, "Arai Y, Koike H, Sato S, Sato Y, Iimura Y, Tani H, Yakushi T, Matushita K, Fuse H, Habe H*.", "Detection of gene mutations possibly related to methanol tolerance in Gluconobacter frateurii mutant Gf398.", "Journal of Environmental Biotechnology 21, 59-62", False),
    (42, 2021, "Habe H, Sato Y, Tani H, Matsutani M, Tanioka K, Theeragool G, Matsushita K, Yakushi T.", "Heterologous expression of membrane-bound alcohol dehydrogenase-encoding genes for glyceric acid production using Gluconobacter sp. CHM43 and its derivatives.", "Appl Microbiol Biotechnol 105, 6749-6758", False),
    (41, 2021, "Takeshita J*, Toyoda A, Tani H, Endo Y, Miyamoto S.", "Classification of chemical compounds based on the correlation between in vitro gene expression profiles.", "Bulletin of Informatics and Cybernetics 53, 1-14", False),
    (40, 2021, "Tani H*, Yamaguchi M, Enomoto Y, Matsumura Y, Habe H, Nakazato T, Kurata S.", "Naked-eye detection of specific DNA sequences amplified by the polymerase chain reaction with nanocomposite beads.", "Anal Biochem 617, 114114", False),
    (39, 2020, "Aoki H*, Tani H, Nakamura K, Sato H, Torimura M, Nakazato T.", "MicroRNA biomarkers for chemical safety screening identified by RNA deep sequencing analysis in mouse embryonic stem cells.", "Toxicol Appl Pharmacol 392, 114929", False),
    (38, 2019, "Tani H*, Numajiri A, Aoki M, Umemura T, Nakazato T.", "Short-lived long noncoding RNAs as surrogate indicators for chemical stress in HepG2 cells and their degradation by nuclear RNases.", "Sci Rep 9, 20299", False),
    (37, 2019, "Tani H*, Matsutani T, Aoki H, Nakamura K, Hamaguchi Y, Nakazato T, Hamada M.", "Identification of RNA biomarkers for chemical safety screening in neural cells derived from mouse embryonic stem cells using RNA deep sequencing analysis.", "Biochem Biophys Res Commun 512, 641-646", False),
    (36, 2017, "Tani H*, Takeshita J, Aoki H, Nakamura K, Abe R, Toyoda A, Endo Y, Miyamoto S, Gamo M, Torimura M, Sato H.", "Effect of methyl p-hydroxybenzoate on the culture of mammalian cell.", "Drug Discov Ther 11, 276-280", False),
    (35, 2017, "Tani H*, Takeshita J, Aoki H, Nakamura K, Abe R, Toyoda A, Endo Y, Miyamoto S, Gamo M, Sato H, Torimura M.", "Identification of RNA biomarkers for chemical safety screening in mouse embryonic stem cells using RNA deep sequencing analysis.", "PLoS One 12, e0182032", False),
    (34, 2017, "Tani H*, Okuda S, Nakamura K, Aoki M, Umemura T.", "Short-lived long non-coding RNAs as surrogate indicators for chemical exposure and LINC00152 and MALAT1 modulate their neighboring genes.", "PLoS One 12, e0181628", False),
    (33, 2017, "Hermawan I, Furuta A, Higashi M, Fujita Y, Akimitsu N, Yamashita A, Moriishi K, Tsuneda S, Tani H, Nakakoshi M, Tsubuki M, Sekiguchi Y, Noda N*, Tanaka J*.", "Four aromatic sulfates with an inhibitory effect against HCV NS3 helicase from the crinoid Alloeocomatella polycladia.", "Mar Drugs 15, E117", False),
    (32, 2017, "Tani H*, Sato H, Torimura M.", "Rapid monitoring of RNA degradation activity in vivo for mammalian cells.", "J Biosci Bioeng 123, 523-527", False),
    (31, 2016, "Tani H*, Takeshita J, Aoki H, Abe R, Toyoda A, Endo Y, Miyamoto S, Gamo M, Torimura M.", "Genome-wide gene expression analysis of mouse embryonic stem cells exposed to p-dichlorobenzene.", "J Biosci Bioeng 122, 329-333", False),
    (30, 2015, "Furuta A, Tsubuki M, Endoh M, Miyamoto T, Tanaka J, Salam KA, Akimitsu N, Tani H, Yamashita A, Moriishi K, Nakakoshi M, Sekiguchi Y, Tsuneda S*, Noda N*.", "Identification of hydroxyanthraquinones as novel inhibitors of hepatitis C virus NS3 helicase.", "Int J Mol Sci 16, 18439-18453", False),
    (29, 2015, "Maekawa S, Imamachi N, Irie T, Tani H, Matsumoto K, Mizutani R, Imamura K, Kakeda M, Yada T, Sugano S, Suzuki Y*, Akimitsu N*.", "Analysis of RNA decay factor mediated RNA stability contributions on RNA abundance.", "BMC Genomics 16, 154", False),
    (28, 2015, "Tani H*, Torimura M.", "Development of cytotoxicity-sensitive human cells using overexpression of long non-coding RNAs.", "J Biosci Bioeng 119, 604-608", False),
    (27, 2015, "Tani H, Imamachi N, Mizutani R, Imamura K, Kwon Y, Miyazaki S, Maekawa S, Suzuki Y, Akimitsu N*.", "Genome-wide analysis of long noncoding RNA turnover.", "Methods Mol Biol 1262, 305-320", False),
    (26, 2015, "Furuta A, Salam KA, Tani H, Tsuneda S, Sekiguchi Y, Akimitsu N, Noda N*.", "A fluorescence-based screening assay for identification of hepatitis C virus NS3 helicase inhibitors and characterization of their inhibitory mechanism.", "Methods Mol Biol 1259, 211-228", False),
    (25, 2014, "Tani H*, Onuma Y, Ito Y, Torimura M.", "Long non-coding RNAs as surrogate indicators for chemical stress responses in human-induced pluripotent stem cells.", "PLoS One 9, e106282", True),
    (24, 2014, "Salam KA, Furuta A, Noda N, Tsuneda S, Sekiguchi Y, Yamashita A, Moriishi K, Nakakoshi M, Tani H, Roy SR, Tanaka J, Tsubuki M*, Akimitsu N*.", "PBDE: structure-activity studies for the inhibition of hepatitis C virus NS3 helicase.", "Molecules 19, 4006-4020", False),
    (23, 2014, "Furuta A, Salam KA, Hermawan I, Akimitsu N, Tanaka J, Tani H, Yamashita A, Moriishi K, Nakakoshi M, Tsubuki M, Peng PW, Suzuki Y, Yamamoto N, Sekiguchi Y, Tsuneda S*, Noda N*.", "Identification and biochemical characterization of halisulfate 3 and suvanine as novel inhibitors of hepatitis C virus NS3 helicase from a marine sponge.", "Mar Drugs 12, 462-476", False),
    (22, 2013, "Tani H*, Torimura M.", "Identification of short-lived long non-coding RNAs as surrogate indicators for chemical stress response.", "Biochem Biophys Res Commun 439, 547-551", False),
    (21, 2014, "Imamachi N, Tani H, Mizutani R, Imamura K, Irie T, Suzuki Y, Akimitsu N*.", "BRIC-seq: a genome-wide approach for determining RNA stability in mammalian cells.", "Methods 67, 55-63", False),
    (20, 2014, "Furuta A, Salam KA, Akimitsu N, Tanaka J, Tani H, Yamashita A, Moriishi K, Nakakoshi M, Tsubuki M, Sekiguchi Y, Tsuneda S*, Noda N*.", "Cholesterol sulfate as a potential inhibitor of hepatitis C virus NS3 helicase.", "J Enzyme Inhib Med Chem 29, 223-229", False),
    (19, 2013, "Salam KA, Furuta A, Noda N, Tsuneda S, Sekiguchi Y, Yamashita A, Moriishi K, Nakakoshi M, Tsubuki M, Tani H, Tanaka J*, Akimitsu N*.", "Psammaplin A inhibits hepatitis C virus NS3 helicase.", "J Nat Med 67, 765-772", False),
    (18, 2013, "Tani H*, Torimura M, Akimitsu N*.", "The RNA degradation pathway regulates the function of GAS5 a non-coding RNA in mammalian cells.", "PLoS One 8, e55684", True),
    (17, 2012, "Fujimoto Y, Salam KA, Furuta A, Matsuda Y, Fujita O, Tani H, Ikeda M, Kato N, Sakamoto N, Maekawa S, Enomoto N, de Voogd NJ, Nakakoshi M, Tsubuki M, Sekiguchi Y, Tsuneda S, Akimitsu N, Noda N, Yamashita A*, Tanaka J*, Moriishi K*.", "Inhibition of both protease and helicase activities of hepatitis C virus NS3 by an ethyl acetate extract of marine sponge Amphimedon sp.", "PLoS One 7, e48685", False),
    (16, 2012, "Tani H, Imamachi N, Salam KA, Mizutani R, Ijiri K, Irie T, Yada T, Suzuki Y, Akimitsu N*.", "Identification of hundreds of novel UPF1 target transcripts by direct determination of whole transcriptome stability.", "RNA Biol 9, 1370-1379", False),
    (15, 2012, "Yamashita A, Salam KA, Furuta A, Matsuda Y, Fujita O, Tani H, Fujita Y, Fujimoto Y, Ikeda M, Kato N, Sakamoto N, Maekawa S, Enomoto N, Nakakoshi M, Tsubuki M, Sekiguchi Y, Tsuneda S, Akimitsu N, Noda N, Tanaka J*, Moriishi K*.", "Inhibition of hepatitis C virus replication and viral helicase by ethyl acetate extract of the marine feather star Alloeocomatella polycladia.", "Mar Drugs 10, 744-761", False),
    (14, 2012, "Mizutani R, Wakamatsu A, Tanaka N, Yoshida H, Tochigi N, Suzuki Y, Oonishi T, Tani H, Tano K, Ijiri K, Isogai T, Akimitsu N*.", "Identification and characterization of novel genotoxic stress-inducible nuclear long noncoding RNAs in mammalian cells.", "PLoS One 7, e34949", False),
    (13, 2012, "Salam KA, Furuta A, Noda N, Tsuneda S, Sekiguchi Y, Yamashita A, Moriishi K, Nakakoshi M, Tsubuki M, Tani H, Tanaka J*, Akimitsu N*.", "Inhibition of hepatitis C virus NS3 helicase by manoalide.", "J Nat Prod 75, 650-654", False),
    (12, 2012, "Tani H, Mizutani R, Salam KA, Tano K, Ijiri K, Wakamatsu A, Isogai T, Suzuki Y, Akimitsu N*.", "Genome-wide determination of RNA stability reveals hundreds of short-lived non-coding transcripts in mammals.", "Genome Res 22, 947-956", True),
    (11, 2010, "Tani H, Nakamura Y, Ijiri K, Akimitsu N*.", "Stability of MALAT-1, a nuclear long non-coding RNA in mammalian cells, varies in various cancer cell.", "Drug Discov Ther 4, 235-239", False),
    (10, 2010, "Tani H, Fujita O, Furuta A, Matsuda Y, Miyata R, Akimitsu N, Tanaka J, Tsuneda S, Sekiguchi Y, Noda N*.", "Real-time monitoring of RNA helicase activity using fluorescence resonance energy transfer in vitro.", "Biochem Biophys Res Commun 393, 131-136", False),
    (9, 2010, "Miyata R, Adachi K, Tani H, Kurata S, Nakamura K, Tsuneda S, Sekiguchi Y, Noda N*.", "Quantitative detection of chloroethene-reductive bacteria Dehalococcoides spp. using alternately binding probe competitive polymerase chain reaction.", "Mol Cell Probes 24, 131-137", False),
    (8, 2009, "Tani H, Miyata R, Ichikawa K, Morishita S, Kurata S, Nakamura K, Tsuneda S, Sekiguchi Y, Noda N*.", "Universal quenching probe system: flexible, specific, and cost-effective real-time PCR method.", "Anal Chem 81, 5678-5685", False),
    (7, 2009, "Morishita S, Tani H, Kurata S, Nakamura K, Tsuneda S, Sekiguchi Y, Noda N*.", "Real-time reverse transcription loop-mediated isothermal amplification for rapid and simple quantification of WT1 mRNA.", "Clin Biochem 42, 515-520", False),
    (6, 2009, "Tani H, Akimitsu N, Fujita O, Matsuda Y, Miyata R, Tsuneda S, Igarashi M, Sekiguchi Y, Noda N*.", "High-throughput screening assay for hepatitis C virus helicase inhibitors using fluorescence-quenching phenomenon.", "Biochem Biophys Res Commun 379, 1054-1059", False),
    (5, 2008, "Noda N*, Tani H, Morita N, Kurata S, Nakamura K, Kanagawa T, Tsuneda S, Sekiguchi Y.", "Estimation of single nucleotide polymorphism allele frequency by alternately binding probe competitive polymerase chain reaction.", "Anal Chim Acta 608, 211-216", False),
    (4, 2007, "Tani H, Kanagawa T, Morita N, Kurata S, Nakamura K, Tsuneda S, Noda N*.", "Calibration-curve-free quantitative PCR (CF-qPCR): a quantitative method for specific nucleic acid sequences without using calibration curves.", "Anal Biochem 369, 105-111", False),
    (3, 2007, "Tani H, Teramura T, Adachi K, Tsuneda S, Kurata S, Nakamura K, Kanagawa T, Noda N*.", "Technique for quantitative detection of specific DNA sequences using alternately binding quenching probe competitive assay combined with loop-mediated isothermal amplification.", "Anal Chem 79, 5608-5613", False),
    (2, 2007, "Tani H, Kanagawa T, Kurata S, Teramura T, Nakamura K, Tsuneda S, Noda N*.", "Quantitative method for specific nucleic acid sequences using competitive polymerase chain reaction with an alternately binding probe.", "Anal Chem 79, 974-979", True),
    (1, 2005, "Tani H, Noda N, Yamada K, Kurata S, Tsuneda S, Hirata A, Kanagawa T*.", "Quantification of genetically modified soybean by quenching probe polymerase chain reaction.", "J Agric Food Chem 53, 2535-2540", False),
]

# --- 総説（英語）Reviews (English)。in press は year=None ---
REVIEWS_EN = [
    (12, None, "Tani H*.", "A blind spot in lncRNA discovery.", "Trends Genet (in press)"),
    (11, None, "Tani H*.", "The half-life of a mark: dwell time and the missing time axis of the epitranscriptome.", "J Mol Biol (in press)"),
    (10, 2026, "Tani H*.", "Half-life as a therapeutic design axis: targeting short-lived lncRNAs with antisense oligonucleotides.", "IUBMB Life 78, e70122"),
    (9, 2026, "Tani H*.", "Short-lived versus long-lived lncRNAs: RNA stability as a determinant of regulatory function.", "Biochim Biophys Acta Gene Regul Mech 1869, 195163"),
    (8, 2025, "Tani H*.", "Biomolecules interacting with long noncoding RNAs.", "Biology 14, 442"),
    (7, 2025, "Tani H*.", "Metabolic labeling of RNA using ribonucleoside analogs enables the evaluation of RNA synthesis and degradation rates.", "Anal Sci 41, 345-351"),
    (6, 2025, "Tani H*.", "RMST: a long noncoding RNA involved in cancer and disease.", "J Biochem 177, 73-78"),
    (5, 2024, "Tani H*.", "Recent advances and prospects in RNA drug development.", "Int J Mol Sci 25, 12284"),
    (4, 2018, "Kurokara R*, Komiya R, Oyoshi T, Matsuno Y, Tani H, Katahira M, et al.", "Multiplicity in long noncoding RNA in living cells.", "Biomedical Sciences 4, 18-23"),
    (3, 2017, "Tani H*.", "Short-lived non-coding transcripts (SLiTs): clues to regulatory long non-coding RNA.", "Drug Discov Ther 11, 20-24"),
    (2, 2012, "Tani H, Akimitsu N*.", "Genome-wide technology for determining RNA stability in mammalian cells: historical perspective and recent advantages based on modified nucleotide labeling.", "RNA Biol 9, 1233-1238"),
    (1, 2012, "Imamachi N, Tani H, Akimitsu N*.", "Up-frameshift protein 1 (UPF1): multitalented entertainer in RNA decay.", "Drug Discov Ther 6, 55-61"),
]

# --- 総説（日本語）Reviews (Japanese) ---
REVIEWS_JP = [
    (10, 2024, "谷英典", "ヒト細胞を用いた化学物質の安全性評価", "化学物質の複合影響と健康リスク評価、医歯薬出版、83-91"),
    (9, 2019, "谷英典", "蛍光色素及び修飾核酸を利用した生体分子解析技術の開発とその応用", "分析化学、2019年2月号、109-116"),
    (8, 2018, "谷英典", "蛍光色素及び修飾核酸を利用した生体分子解析技術の開発とその応用", "ぶんせき、2018年8月号、342"),
    (7, 2018, "谷英典", "ノンコーディングRNAから生命の謎を解き明かす", "PHARM TECH JAPAN、2018年5月号、18-19"),
    (6, 2018, "谷英典", "ヒトiPS細胞を用いた水質安全性評価のシステム", "PHARM TECH JAPAN、2018年3月号、125-128"),
    (5, 2017, "谷英典", "次世代シークエンサーによるノンコーディングRNAの解析", "ぶんせき、2017年10月号、456-458"),
    (4, 2017, "谷英典", "ヒト細胞を用いた化学物質の安全性評価", "製品含有化学物質のリスク管理、情報伝達の効率化、技術情報協会、239-245"),
    (3, 2016, "谷英典", "ノンコーディングRNA動態解明の最前線", "ぶんせき、2016年6月号、213-214"),
    (2, 2012, "谷英典、水谷玲菜、鈴木穣、秋光信佳", "RNAの安定性を指標にして機能不明な長鎖ノンコーディングRNAの性質を定義する", "細胞工学、秀潤社、Vol.31, No.8, 926-927"),
    (1, 2009, "野田尚宏、関口勇地、松田泰嘉、谷英典、常田聡", "メタゲノム解析におけるFunction-based screening法の高度化", "マリンメタゲノムの有効利用、シーエムシー出版、28-40"),
]

# --- 外部グラント External Grants（新しい順） ---
GRANTS = [
    ("2017 – 2022", "経済産業省 委託事業", "Commissioned project, Ministry of Economy, Trade and Industry (METI)"),
    ("2017 – 2019", "科学研究費補助金 若手研究(B)", "JSPS KAKENHI, Grant-in-Aid for Young Scientists (B)"),
    ("2015 – 2016", "クリタ水・環境科学振興財団 国内研究助成", "Kurita Water and Environment Foundation, domestic research grant"),
    ("2015 – 2018", "科学研究費補助金 基盤研究(B)（分担）", "JSPS KAKENHI, Grant-in-Aid for Scientific Research (B), co-investigator"),
    ("2014 – 2016", "科学研究費補助金 若手研究(B)", "JSPS KAKENHI, Grant-in-Aid for Young Scientists (B)"),
    ("2012 – 2015", "JST 復興促進プログラム", "JST Reconstruction Promotion Program"),
    ("2009 – 2012", "科学研究費補助金 特別研究員奨励費（PD）", "JSPS KAKENHI, Grant-in-Aid for JSPS Research Fellow (PD)"),
    ("2007 – 2009", "科学研究費補助金 特別研究員奨励費（DC2）", "JSPS KAKENHI, Grant-in-Aid for JSPS Research Fellow (DC2)"),
]

# --- 招待講演 Invited Lectures ---
TALKS_INTL = [
    (2014, "Tani H.", "Long non-coding RNAs as surrogate indicators for environmental stress response in human cells.", "Workshop on Advanced Technologies for Wastewater Reclamation and Reuse, Beijing, China (Oral)"),
]
TALKS_DOM = [
    (2025, "谷英典", "医薬品開発に向けた長鎖ノンコーディングRNAの機能解明", "第48回日本分子生物学会年会、横浜、2025年12月"),
    (2025, "谷英典", "医薬品開発に向けた長鎖ノンコーディングRNAの機能解明", "RNA勉強会 第8回（星薬科大学）、東京、2025年6月"),
    (2025, "谷英典", "長鎖ノンコーディングRNAに着目した革新的なRNA創薬", "BVAバイオインターフェース（オンライン）、2025年3月"),
    (2024, "谷英典", "隠されていたRNAワールド", "マリンバイオテクノロジー学会 若手の会（東京農工大学）、東京、2024年11月"),
    (2024, "谷英典", "慢性肝疾患と長鎖ノンコーディングRNAに関する論文", "著者による論文ゼミ 2024、オンライン、2024年9月"),
    (2022, "谷英典", "non-coding RNAをバイオマーカーとする化学物質の毒性評価予測", "環境エピゲノミクス研究会（EEG）ネットシンポジウム、オンライン、2022年10月"),
    (2022, "谷英典", "ノンコーディングRNAをエンドポイントとする化学物質の毒性評価予測", "幹細胞を用いた化学物質リスク情報共有化コンソーシアム 年会、京都、2022年3月"),
    (2018, "谷英典", "蛍光色素及び修飾核酸を利用した生体分子解析技術の開発とその応用", "第67回日本分析化学会年会、仙台、2018年9月"),
    (2018, "谷英典", "長鎖ノンコーディングRNAに関するRNA分解からのアプローチ", "第2回長鎖非コードRNA勉強会、東京、2018年5月"),
    (2017, "谷英典", "ノンコーディングRNAに着目した化学物質の生体影響評価技術の開発", "京都大学iPS細胞研究所セミナー、京都、2017年11月"),
    (2017, "谷英典", "長鎖ノンコーディングRNAに関するRNA分解からのアプローチ", "第1回長鎖非コードRNA勉強会、東京、2017年5月"),
    (2016, "谷英典", "大規模ノンコーディングRNA解析を可能とする次世代シーケンサの活用", "第76回分析化学討論会、岐阜、2016年5月"),
    (2013, "秋光信佳（今村亮俊, 谷英典 ほか）", "RNA安定性調節を介した遺伝子発現システムの制御", "第36回日本分子生物学会、神戸、2013年12月"),
    (2013, "谷英典", "BRIC-seq：ゲノムワイドなRNA分解測定法を用いた新規UPF1標的RNAの同定", "第36回日本分子生物学会、神戸、2013年12月"),
    (2013, "谷英典", "長鎖ノンコーディングRNAが操る生命現象", "医薬創製教育研究センター特別講演会（徳島大学）、徳島、2013年7月"),
    (2013, "谷英典", "研究紹介", "早稲田大学、東京、2013年3月"),
    (2012, "谷英典", "研究紹介", "早稲田大学、東京、2012年12月"),
    (2010, "谷英典", "蛍光消光現象を利用した生体分子解析技術の開発", "産業技術総合研究所、つくば、2010年10月"),
]

# --- 主要業績に選ぶ原著の番号（★著者指定＋高被引用＋近年・機構代表） ---
SELECTED_ORIGINALS = [49, 38, 34, 27, 25, 21, 18, 16, 12, 8, 3, 2]
