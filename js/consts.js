// 背景列表
const backgrounds = {
    "c1": {"name": "C1"},
    "c2": {"name": "C2"},
    "c3": {"name": "C3"},
    "c4": {"name": "C4"},
    "c5": {"name": "C5"},
    "c6": {"name": "C6"},
    "c7": {"name": "C7"},
    "c8": {"name": "C8"},
    "c9": {"name": "C9"},
    "c10": {"name": "C10"},
    "c11": {"name": "C11"},
    "c12": {"name": "C12"},
    "c13": {"name": "C13"},
    "c14": {"name": "C14"},
    "c15": {"name": "C15"},
    "c16": {"name": "C16"}
};

// 角色配置字典
const mahoshojo = {
    "ema":    {"name": "樱羽艾玛", "emotion_count": 8},
    "hiro":   {"name": "二阶堂希罗", "emotion_count": 6},
    "sherri": {"name": "橘雪莉", "emotion_count": 7},
    "hanna":  {"name": "远野汉娜", "emotion_count": 5},
    "anan":   {"name": "夏目安安", "emotion_count": 9},
    "yuki" :  {"name": "月代雪", "emotion_count": 18},
    "meruru": {"name": "冰上梅露露", "emotion_count": 6},
    "noa":    {"name": "城崎诺亚", "emotion_count": 6},
    "reia":   {"name": "莲见蕾雅", "emotion_count": 7},
    "miria":  {"name": "佐伯米莉亚", "emotion_count": 4},
    "nanoka": {"name": "黑部奈叶香", "emotion_count": 5},
    "mago":   {"name": "宝生玛格", "emotion_count": 5},
    "alisa":  {"name": "紫藤亚里沙", "emotion_count": 6},
    "coco":   {"name": "泽渡可可", "emotion_count": 5}
};

// 角色文字配置字典 - 每个角色对应4个文字配置
const text_configs_dict = {
    "nanoka": [  // 黑部奈叶香
        {"text":"黑","position":[759,63],"font_color":[131,143,147],"font_size":196},
        {"text":"部","position":[955,175],"font_color":[255,255,255],"font_size":92},
        {"text":"奈","position":[1053,117],"font_color":[255,255,255],"font_size":147},
        {"text":"叶香","position":[1197,175],"font_color":[255,255,255],"font_size":92}
    ],
    "hiro": [    // 二阶堂希罗
        {"text":"二","position":[759,63],"font_color":[239,79,84],"font_size":196},
        {"text":"阶堂","position":[955,175],"font_color":[255,255,255],"font_size":92},
        {"text":"希","position":[1143,110],"font_color":[255,255,255],"font_size":147},
        {"text":"罗","position":[1283,175],"font_color":[255,255,255],"font_size":92}
    ],
    "ema": [     // 樱羽艾玛
        {"text":"樱","position":[759,73],"font_color":[253,145,175],"font_size":186},
        {"text":"羽","position":[949,175],"font_color":[255,255,255],"font_size":92},
        {"text":"艾","position":[1039,117],"font_color":[255,255,255],"font_size":147},
        {"text":"玛","position":[1183,175],"font_color":[255,255,255],"font_size":92}
    ],
    "sherri": [  // 橘雪莉
        {"text":"橘","position":[759,73],"font_color":[137,177,251],"font_size":186},
        {"text":"雪","position":[943,110],"font_color":[255,255,255],"font_size":147},
        {"text":"莉","position":[1093,175],"font_color":[255,255,255],"font_size":92}/*,
        {"text":"","position":[0,0],"font_color":[255,255,255],"font_size":1} */
    ],
    "anan": [    // 夏目安安
        {"text":"夏","position":[759,73],"font_color":[159,145,251],"font_size":186},
        {"text":"目","position":[949,175],"font_color":[255,255,255],"font_size":92},
        {"text":"安","position":[1039,117],"font_color":[255,255,255],"font_size":147},
        {"text":"安","position":[1183,175],"font_color":[255,255,255],"font_size":92}
    ],
    "noa": [     // 城崎诺亚
        {"text":"城","position":[759,73],"font_color":[104,223,231],"font_size":186},
        {"text":"崎","position":[945,175],"font_color":[255,255,255],"font_size":92},
        {"text":"诺","position":[1042,117],"font_color":[255,255,255],"font_size":147},
        {"text":"亚","position":[1186,175],"font_color":[255,255,255],"font_size":92}
    ],
    "coco": [    // 泽渡可可
        {"text":"泽","position":[759,73],"font_color":[251,114,78],"font_size":186},
        {"text":"渡","position":[945,175],"font_color":[255,255,255],"font_size":92},
        {"text":"可","position":[1042,117],"font_color":[255,255,255],"font_size":147},
        {"text":"可","position":[1186,175],"font_color":[255,255,255],"font_size":92}
    ],
    "alisa": [   // 紫藤亚里沙
        {"text":"紫","position":[759,73],"font_color":[235,75,60],"font_size":186},
        {"text":"藤","position":[945,175],"font_color":[255,255,255],"font_size":92},
        {"text":"亚","position":[1042,117],"font_color":[255,255,255],"font_size":147},
        {"text":"里沙","position":[1186,175],"font_color":[255,255,255],"font_size":92}
    ],
    "reia": [    // 莲见蕾雅
        {"text":"莲","position":[759,73],"font_color":[253,177,88],"font_size":186},
        {"text":"见","position":[945,175],"font_color":[255,255,255],"font_size":92},
        {"text":"蕾","position":[1042,117],"font_color":[255,255,255],"font_size":147},
        {"text":"雅","position":[1186,175],"font_color":[255,255,255],"font_size":92}
    ],
    "mago": [    // 宝生玛格
        {"text":"宝","position":[759,73],"font_color":[185,124,235],"font_size":186},
        {"text":"生","position":[945,175],"font_color":[255,255,255],"font_size":92},
        {"text":"玛","position":[1042,117],"font_color":[255,255,255],"font_size":147},
        {"text":"格","position":[1186,175],"font_color":[255,255,255],"font_size":92}
    ],
    "hanna": [   // 远野汉娜
        {"text":"远","position":[759,73],"font_color":[169,199,30],"font_size":186},
        {"text":"野","position":[945,175],"font_color":[255,255,255],"font_size":92},
        {"text":"汉","position":[1042,117],"font_color":[255,255,255],"font_size":147},
        {"text":"娜","position":[1186,175],"font_color":[255,255,255],"font_size":92}
    ],
    "meruru": [  // 冰上梅露露
        {"text":"冰","position":[759,73],"font_color":[227,185,175],"font_size":186},
        {"text":"上","position":[945,175],"font_color":[255,255,255],"font_size":92},
        {"text":"梅","position":[1042,117],"font_color":[255,255,255],"font_size":147},
        {"text":"露露","position":[1186,175],"font_color":[255,255,255],"font_size":92}
    ],
    "miria": [   // 佐伯米莉亚
        {"text":"佐","position":[759,73],"font_color":[235,207,139],"font_size":186},
        {"text":"伯","position":[945,175],"font_color":[255,255,255],"font_size":92},
        {"text":"米","position":[1042,117],"font_color":[255,255,255],"font_size":147},
        {"text":"莉亚","position":[1186,175],"font_color":[255,255,255],"font_size":92}
    ],
    "yuki": [    // 月代雪
        {"text":"月","position":[759,63],"font_color":[195,209,231],"font_size":196},
        {"text":"代","position":[948,175],"font_color":[255,255,255],"font_size":92},
        {"text":"雪","position":[1053,117],"font_color":[255,255,255],"font_size":147}/*,
        {"text":"","position":[0,0],"font_color":[255,255,255],"font_size":1}*/
    ]
};

const text_postion = [728,355]; // 文本范围起始位置
const text_over = [2339,800];  // 文本范围右下角位置
const shadow_offset = [2, 2]; // 阴影偏移量
const shadow_color = [0, 0, 0]; // 黑色阴影
