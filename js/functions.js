const text_postion = [728,355]; // 文本范围起始位置
const text_over = [2339,800];  // 文本范围右下角位置
const shadow_offset = [2, 2]; // 阴影偏移量
const shadow_color = [0, 0, 0]; // 黑色阴影

// 角色配置字典
var mahoshojo = {};
// 角色文字配置字典
var text_configs = {};

function initBackgrounds() {
    // 渲染背景选择
    let backgrounds_div = $("#backgrounds_div");
    backgrounds_div.empty();

    // 背景列表
    const backgrounds = ["c1","c2","c3","c4","c5","c6","c7","c8","c9","c10","c11","c12","c13","c14","c15","c16"];

    for (const key of backgrounds) {
        let bg_html = `
        <div class="col-6 col-md-3">
            <label class="form-imagecheck mb-2">
                <input name="background" type="radio" value="${key}" class="form-imagecheck-input" onchange="updateCanvas()" onclick="updateCanvas()"${key=="c15" ? " checked" : ""}/>
                <span class="form-imagecheck-figure">
                    <img class="form-imagecheck-image" src="./assets/background/${key}.png"/>
                </span>
            </label>
        </div>
        `;
        backgrounds_div.append(bg_html);
    }
}
function initCharacters() {
    // 渲染角色选择
    let characters_div = $("#characters_div");
    characters_div.empty();
    for (const [key, value] of Object.entries(mahoshojo)) {
        let char_html = `
        <div class="col-auto">
            <label class="form-imagecheck mb-2">
                <input name="character" type="radio" value="${key}" class="form-imagecheck-input" onchange="initEmotions('${key}');updateCanvas()" onclick="initEmotions('${key}');updateCanvas()"${key=="sherri" ? " checked" : ""}/>
                <span class="form-imagecheck-figure">
                    <span class="avatar avatar-xl" style="background-image: url('./assets/chara/${key}/${key} (1).png')" title="${value.full_name}" data-bs-toggle="tooltip"></span>
                </span>
            </label>
        </div>
        `;
        characters_div.append(char_html);
    }
}
function initEmotions(character) {
    // 渲染表情选择
    let emotions_div = $("#emotions_div");
    emotions_div.empty();
    for (i=1; i<mahoshojo[character].emotion_count; i++) {
        let emotion_html = `
        <div class="col-auto">
            <label class="form-imagecheck mb-2">
                <input name="emotion" type="radio" value="${i}" class="form-imagecheck-input" onchange="updateCanvas()" onclick="updateCanvas()"/>
                <span class="form-imagecheck-figure">
                    <img class="form-imagecheck-image avatar avatar-xl" src="./assets/chara/${character}/${character} (${i}).png"/>
                </span>
            </label>
        </div>
        `;
        emotions_div.append(emotion_html);
    }
    $('input[name="emotion"]').first().click();
}
function updateCanvas() {
    let canvas = $('#canvas')[0];
    let ctx = canvas.getContext("2d");

    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if ($('input[name="background"]:checked')) ctx.drawImage($('input[name="background"]:checked').next().children()[0], 0, 0, canvas.width, canvas.height);
    
    let character = $('input[name="character"]:checked').val();
    if (character) {
        if ($('input[name="emotion"]:checked')) ctx.drawImage($('input[name="emotion"]:checked').next().children()[0], 0, 134);
        for (const [key, value] of Object.entries(text_configs[character])) {
            ctx.font = `${value.font_size}px font3`;

            ctx.fillStyle = `rgb(${shadow_color[0]}, ${shadow_color[1]}, ${shadow_color[2]})`;
            ctx.fillText(value.text, value.position[0] + shadow_offset[0], value.font_size + value.position[1] + shadow_offset[1]);

            ctx.fillStyle = `rgb(${value.font_color[0]}, ${value.font_color[1]}, ${value.font_color[2]})`;
            ctx.fillText(value.text, value.position[0], value.font_size + value.position[1]);
        }
    }

    let text = $('input[name="text"]').val();
    if (text) {
        let text_font_size = parseInt($('input[name="text_font_size"]').val());
        ctx.font = `${text_font_size}px ${mahoshojo[character].font}`;
        
        // 自动换行绘制
        const maxWidth = text_over[0] - text_postion[0];
        const maxHeight = text_over[1] - text_postion[1];
        const lineHeight = Math.floor(text_font_size * 1.2);
        const maxLines = Math.floor(maxHeight / lineHeight) || 1;
        let lines = [];

        // 根据空格进行单词换行，若无空格则按字符换行（适合中文）
        if (text.indexOf(' ') !== -1) {
            const words = text.split(' ');
            let line = '';
            for (let n = 0; n < words.length; n++) {
                const testLine = line ? (line + ' ' + words[n]) : words[n];
                const testWidth = ctx.measureText(testLine).width;
                if (testWidth > maxWidth && line) {
                    lines.push(line);
                    line = words[n];
                    if (lines.length >= maxLines) break;
                } else {
                    line = testLine;
                }
            }
            if (lines.length < maxLines && line) lines.push(line);
        } else {
            let line = '';
            for (let i = 0; i < text.length; i++) {
                const ch = text[i];
                const testLine = line + ch;
                const testWidth = ctx.measureText(testLine).width;
                if (testWidth > maxWidth && line) {
                    lines.push(line);
                    line = ch;
                    if (lines.length >= maxLines) break;
                } else {
                    line = testLine;
                }
            }
            if (lines.length < maxLines && line) lines.push(line);
        }

        // 绘制每一行（先阴影再主体）
        for (let i = 0; i < Math.min(lines.length, maxLines); i++) {
            const line = lines[i];
            const x = text_postion[0];
            // 保持与原来单行位置一致：首行基线为 text_font_size + text_postion[1]
            const y = text_font_size + text_postion[1] + i * lineHeight;

            ctx.fillStyle = `rgb(${shadow_color[0]}, ${shadow_color[1]}, ${shadow_color[2]})`;
            ctx.fillText(line, x + shadow_offset[0], y + shadow_offset[1]);

            ctx.fillStyle = `rgb(255, 255, 255)`;
            ctx.fillText(line, x, y);
        }

        // 突出显示【文本】部分
        let isHighlight = false;
        for (let i = 0; i < Math.min(lines.length, maxLines); i++) {
            const line = lines[i];
            const x = text_postion[0];
            // 保持与原来单行位置一致：首行基线为 text_font_size + text_postion[1]
            const y = text_font_size + text_postion[1] + i * lineHeight;

            // 检查并切换绘制颜色
            const parts = line.split(/(【|】)/g);
            let currentX = x;

            parts.forEach(part => {
                if (part === '【' || part === '】') {
                    isHighlight = true;
                }
                if (isHighlight) {
                    ctx.fillStyle = `rgb(${text_configs[character][0]['font_color'][0]},${text_configs[character][0]['font_color'][1]},${text_configs[character][0]['font_color'][2]})`
                    ctx.fillText(part, currentX, y); // 绘制高亮显示的文本
                    currentX += ctx.measureText(part).width; // 更新当前X坐标
                } else {
                    currentX += ctx.measureText(part).width; // 更新当前X坐标
                }
                if (part === '】') {
                    isHighlight = false;
                }
            });
        }
    }
}
function downloadImage() {
    let canvas = $('#canvas')[0];
    canvas.toBlob(function(blob) {
        saveAs(blob, `魔裁文本框表情-${Date.now()}.png`);
    });
}
function checkConfigs(direct=false, chara_meta_yaml="", text_configs_yaml="") {
    if (direct) {
        if (chara_meta_yaml == "" || text_configs_yaml == "") {
            $.when(
                $.get("./config/chara_meta.yml", function(data) {
                    chara_meta_yaml = data;
                }).fail(function(e) {
                    console.warn("读取 chara_meta.yml 失败：", e);
                    checkConfigs(false);
                }),
                $.get("./config/text_configs.yml", function(data) {
                    text_configs_yaml = data;
                }).fail(function(e) {
                    console.warn("读取 text_configs.yml 失败：", e);
                    checkConfigs(false);
                })
            ).done(function() {
                if (chara_meta_yaml == "" || text_configs_yaml == "") {
                    console.info("未能通过 YAML 直读加载配置，尝试从本地存储加载。");
                    checkConfigs(false);
                } else {
                    checkConfigs(true, chara_meta_yaml, text_configs_yaml);
                }
            });
        }
    } else {
        chara_meta_yaml = localStorage.getItem("manosaba_chara_meta") ?? "";
        text_configs_yaml = localStorage.getItem("manosaba_text_configs") ?? "";
    }

    mahoshojo = chara_meta_yaml ? jsyaml.load(chara_meta_yaml)['mahoshojo'] : {};
    text_configs = text_configs_yaml ? jsyaml.load(text_configs_yaml)['text_configs'] : {};
    $('#chara_meta').val(chara_meta_yaml);
    $('#text_configs').val(text_configs_yaml);
    if (Object.keys(mahoshojo).length > 0) {
        for (const [key, value] of Object.entries(mahoshojo)) {
            value.font = value.font.replace(".ttf", "");
        }
        $('#chara_meta-indicator').html(`<span class="text-success">已加载 ${Object.keys(mahoshojo).length} 条${direct ? "（YAML 直读）" : ""}</span>`);
    } else {
        $('#chara_meta-indicator').html('<span class="text-danger">未加载</span>');
    }
    if (Object.keys(text_configs).length > 0) {
        $('#text_configs-indicator').html(`<span class="text-success">已加载 ${Object.keys(text_configs).length} 条${direct ? "（YAML 直读）" : ""}</span>`);
    } else {
        $('#text_configs-indicator').html('<span class="text-danger">未加载</span>');
    }
    
    $('ul.nav.nav-tabs.card-header-tabs li, ul.nav.nav-tabs.card-header-tabs li > a').removeClass("active");
    if (Object.keys(mahoshojo).length > 0 && Object.keys(text_configs).length > 0) {
        initBackgrounds();
        initCharacters();
        initEmotions('sherri');
        $('ul.nav.nav-tabs.card-header-tabs li').removeAttr("hidden");
        $('ul.nav.nav-tabs.card-header-tabs li:nth-child(2), ul.nav.nav-tabs.card-header-tabs li:nth-child(2) > a').addClass("active");
        $('.tab-pane').removeClass("active show");
        $('#tabs-chara').addClass("active show");
        $('#preview_div').show();
        if (direct) {
            $('#configs_upload_div').html("已经通过 YAML 文件直接加载配置，无需上传。");
        }
    } else {
        $('ul.nav.nav-tabs.card-header-tabs li').attr("hidden", true);
        $('ul.nav.nav-tabs.card-header-tabs li:nth-child(3)').removeAttr("hidden");
        $('ul.nav.nav-tabs.card-header-tabs li:nth-child(3), ul.nav.nav-tabs.card-header-tabs li:nth-child(3) > a').addClass("active");
        $('.tab-pane').removeClass("active show");
        $('#tabs-settings').addClass("active show");
        $('#preview_div').hide();
    }
}
function resetConfigs() {
    localStorage.removeItem("manosaba_chara_meta");
    localStorage.removeItem("manosaba_text_configs");
    checkConfigs();
}
function init() {
    checkConfigs(true);
}
$(document).ready(function() {
    init();
    $('input[name="configs"]').on('change', function(event) {
        const files = event.target.files;
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const reader = new FileReader();
            reader.onload = function(e) {
                const content = e.target.result;
                try {
                    const data = jsyaml.load(content);
                    if (file.name === "chara_meta.yml") {
                        $('#chara_meta').val(content);
                        localStorage.setItem("manosaba_chara_meta", content);
                    } else if (file.name === "text_configs.yml") {
                        $('#text_configs').val(content);
                        localStorage.setItem("manosaba_text_configs", content);
                    } else {
                        console.info("已跳过未知的配置文件：" + file.name);
                    }
                } catch (error) {
                    console.warn("解析 " + file.name + " 失败：" + error);
                }
                checkConfigs();
            };
            reader.readAsText(file);
        }
    });
});