let plants = [];
let currentPlant = null;
let currentWeatherInfo = "未知";
const API_URL = "https://rivka-gablewindowed-micki.ngrok-free.dev"; // 後端網址

// --- 登入系統 ---
async function login(){
  let u = document.getElementById("username").value.trim();
  let p = document.getElementById("password").value.trim();
  
  try {
    const response = await fetch(`${API_URL}/api/login`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "69420" // 這一行可以強制跳過 ngrok 警告頁面
      },
      body: JSON.stringify({ email: u, password: p })
    });

    if (response.ok) {
      enterMainPage(u);
    } else {
      document.getElementById("loginMsg").innerText = "帳號或密碼錯誤 ❌";
    }
  } catch (error) {
    console.error("錯誤詳情:", error);
    let users = JSON.parse(localStorage.getItem("users") || "[]");
    let found = users.find(user => user.username === u && user.password === p);
    if (found) enterMainPage(u);
    else document.getElementById("loginMsg").innerText = "帳號錯誤或伺服器未啟動";
  }
}

function enterMainPage(u) {
  document.getElementById("loginPage").classList.add("hidden");
  document.getElementById("mainPage").classList.remove("hidden");
  document.getElementById("welcome").innerText = "歡迎 " + u + " 🌱";
  plants = JSON.parse(localStorage.getItem("plants_" + u) || "[]");
  renderPlants();
  openModal("guideModal");
}

function logout(){
  saveData();
  location.reload();
}

function saveData(){
  let u = document.getElementById("welcome").innerText.replace("歡迎 ","").replace(" 🌱","");
  if(u) localStorage.setItem("plants_" + u, JSON.stringify(plants));
}

// --- 註冊與密碼 ---
async function register(){
  let u = document.getElementById("regUsername").value.trim();
  let p = document.getElementById("regPassword").value.trim();
  let cp = document.getElementById("regConfirmPassword").value.trim();
  let msg = document.getElementById("regMsg");
  
  if(!u || !p){ msg.innerText="帳號密碼不可空白"; return; }
  if(p !== cp){ msg.innerText="密碼不一致 ❌"; return; }

  try {
    const response = await fetch(`${API_URL}/api/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: u, password: p })
    });

    if (response.ok) {
      msg.style.color="green";
      msg.innerText="註冊成功 ✅";
      setTimeout(closeAllModal, 1000);
    } else {
      msg.innerText="帳號已存在或伺服器錯誤";
    }
  } catch (error) {
    let users = JSON.parse(localStorage.getItem("users") || "[]");
    if(users.find(user=>user.username===u)){ msg.innerText="帳號已存在"; return; }
    users.push({username:u, password:p});
    localStorage.setItem("users", JSON.stringify(users));
    msg.style.color="green";
    msg.innerText="本地註冊成功 ✅";
    setTimeout(closeAllModal, 1000);
  }
}

function togglePassword(id) {
  const input = document.getElementById(id);
  input.type = input.type === "password" ? "text" : "password";
}

// --- Modal 控制 ---
function openModal(id){ closeAllModal(); document.getElementById(id).classList.add("show"); }
function closeAllModal(){ document.querySelectorAll(".modal").forEach(m=>m.classList.remove("show")); }
window.onclick = function(e){ if(e.target.classList.contains("modal")) closeAllModal(); }

// --- 植物渲染 ---
// --- 1. 修改原本的渲染函數 (變成橫條世界列表) ---
function renderPlants(){
  let list = document.getElementById("plantList"); 
  list.innerHTML = "";
  
  // 確保回到列表時，顯示列表隱藏內頁
  document.getElementById("worldListArea").classList.remove("hidden");
  document.getElementById("detailView").classList.add("hidden");

  plants.forEach((p, i) => {
    let div = document.createElement("div"); 
    div.className = "plantCard";
    
    // 點擊整個橫條就「進入世界」
    div.onclick = () => enterWorld(i);

    div.innerHTML = `
      <div>
        <h3 style="margin:0;">${p.name}</h3>
        <p style="margin:5px 0 0; font-size:0.8em; color:#aaa;">生長天數 | 第 ${getDays(p)} 天</p>
      </div>
      <div style="font-size:1.2em;">➡️</div>
    `;
    list.appendChild(div);
  });
}

// --- 2. 新增：進入特定植物的世界 (內頁) ---
function enterWorld(i) {
  currentPlant = i;
  let p = plants[i];
  
  // 切換頁面顯示
  document.getElementById("worldListArea").classList.add("hidden");
  document.getElementById("detailView").classList.remove("hidden");
  
  // 設定內頁標題與資訊
  document.getElementById("viewingPlantName").innerText = p.name;
  document.getElementById("plantStatusInfo").innerHTML = `<h3>陪伴第 ${getDays(p)} 天</h3>`;
  
  // 渲染內頁的最新日記
  updateDetailView();
}

// --- 3. 新增：更新內頁顯示 ---
function updateDetailView() {
  let p = plants[currentPlant];
  let container = document.getElementById("latestDiaryInView");
  container.innerHTML = "";

  if(p.diary && p.diary.length > 0) {
    let latest = p.diary[p.diary.length - 1];
    container.innerHTML = `
      <div class="latest-diary">
        <strong>最新紀錄 (${latest.date.split("T")[0]})：</strong><br>
        ${latest.text}<br>
        <small>${latest.weather}</small>
        ${latest.img ? `<img src="${latest.img}" style="width:100%; border-radius:10px; margin-top:10px;">` : ''}
      </div>
    `;
  } else {
    container.innerHTML = `<p style="color:#999; margin-top:20px;">這個世界還沒有日記紀錄...</p>`;
  }
}

// --- 4. 輔助切換功能 ---
function backToWorlds() {
  renderPlants(); // 重新整理列表並顯示
}

function openDiaryFromView() {
  document.getElementById("aiReply").innerText = "";
  openModal("diaryModal");
  getWeather(); // 呼叫你原本的天氣抓取
}

function deleteCurrentPlant() {
    if(confirm("確定要刪除這個世界嗎？所有的紀錄都會消失！")) {
        plants.splice(currentPlant, 1);
        saveData();
        backToWorlds();
    }
}

// 替換原本的 addPlant 函數
async function addPlant(){
    let name = document.getElementById("plantName").value.trim();
    let startDateInput = document.getElementById("setupStartDate").value;
    
    if(!name) return alert("請輸入植物名稱喔！");
    if(!startDateInput) return alert("請選擇開始種植日期！");

    let water = document.getElementById("setupWater").value;
    let appearances = Array.from(document.querySelectorAll('.setupAppearance:checked')).map(cb => cb.value).join("、");
    if(!appearances) appearances = "無特別狀況";
    let bloom = document.querySelector('input[name="setupBloom"]:checked').value;
    let fruit = document.querySelector('input[name="setupFruit"]:checked').value;
    let sun = document.getElementById("setupSun").value;
    let setupRecordText = `【初始狀態紀錄】\n💧 澆水：${water}\n🌿 外觀：${appearances}\n🌸 開花：${bloom}\n🍅 結果：${fruit}\n☀️ 日照：${sun}`;

    let start = new Date(startDateInput);
    let now = new Date();
    let dayDiff = Math.floor((now - start) / (1000 * 60 * 60 * 24)) + 1;

    const email = localStorage.getItem("email");

    // 串接後端
    try {
        const res = await fetch(`${API_URL}/api/addPlant`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "ngrok-skip-browser-warning": "69420"
            },
            body: JSON.stringify({
                email: email,
                name: name,
                species: "聖女番茄",
                start_date: startDateInput
            })
        });
        const data = await res.json();
        console.log("新增植物:", data);
    } catch(e) {
        console.error("新增植物失敗:", e);
    }

    let newPlant = {
        name: name,
        startDate: start.toISOString(),
        baseDay: 0,
        diary: [{
            date: new Date().toISOString(),
            day: dayDiff,
            text: setupRecordText,
            weather: "初始設定",
            img: null
        }]
    };

    plants.push(newPlant);
    saveData();
    renderPlants();
    closeAllModal();

    document.getElementById("plantName").value = "";
    document.getElementById("setupStartDate").value = "";
    document.querySelectorAll('.setupAppearance').forEach(cb => cb.checked = false);
}

function deletePlant(i){ 
  if(confirm("確定要刪除這株植物嗎？")) { plants.splice(i,1); saveData(); renderPlants(); } 
}

// --- 天氣系統 ---
function openDiary(i){ 
  currentPlant=i; 
  document.getElementById("aiReply").innerText = "";
  openModal("diaryModal"); 
  getWeather(); 
}

function getWeather(){
  const display = document.getElementById("weatherDisplay");
  const citySelect = document.getElementById("citySelect");
  display.innerText = "正在定位中...";
  citySelect.style.display = "none";
  if (!navigator.geolocation) {
    display.innerText = "🌤️ 瀏覽器不支援定位";
    citySelect.style.display = "block";
    return;
  }
  navigator.geolocation.getCurrentPosition(async pos=>{
    fetchWeatherAPI(pos.coords.latitude, pos.coords.longitude);
  }, () => {
    display.innerText = "🌤️ 定位失敗，請手動選擇";
    citySelect.style.display = "block";
  }, { timeout: 5000 });
}

async function getWeatherByCity() {
  const val = document.getElementById("citySelect").value;
  if(!val) return;
  const [lat, lon] = val.split(",");
  fetchWeatherAPI(lat, lon);
}

async function fetchWeatherAPI(lat, lon) {
  const display = document.getElementById("weatherDisplay");
  try {
    let res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&hourly=relative_humidity_2m,uv_index&timezone=auto`);
    let data = await res.json();
    const hour = new Date().getHours();
    const temp = data.current_weather.temperature;
    const hum = data.hourly.relative_humidity_2m[hour];
    const uv = data.hourly.uv_index[hour];
    currentWeatherInfo = `${temp}°C / 濕度:${hum}% / UV:${uv}`;
    let advice = uv > 6 ? "⚠️ 紫外線強，建議遮蔭" : (hum > 80 ? "💧 濕度高，注意通風" : "🌤️ 環境適合成長");
    display.innerHTML = `🌡️ ${temp}°C | 💧 ${hum}% | ☀️ UV:${uv}<br><span style="color:green">${advice}</span>`;
  } catch(e) { display.innerText = "🌤️ 取得氣象失敗"; }
}

// --- 儲存日記 (對接後端) ---
// --- 儲存日記 (對接後端) ---
async function saveDiary(){
    let text = document.getElementById("diaryText").value;
    let fileInput = document.getElementById("photo");
    let file = fileInput.files[0];
    const email = localStorage.getItem("email");

    const doSave = async (imgResult = null) => {
        let p = plants[currentPlant];
        const newEntry = {
            email: email,
            plant_name: p.name,  // 改成小寫 n
            text: text,
            weather: currentWeatherInfo,
            date: new Date().toISOString(),
            day: getDays(p),
            img: imgResult
        };

        try {
            document.getElementById("aiReply").innerText = "⏳ 正在儲存並取得 AI 回覆...";
            
            // 儲存日記
            const res = await fetch(`${API_URL}/api/saveRecord`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "ngrok-skip-browser-warning": "69420"
                },
                body: JSON.stringify(newEntry)
            });

            if (res.ok) {
                // 取得 AI 回覆
                const aiRes = await fetch(`${API_URL}/api/analyzeDiary`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "ngrok-skip-browser-warning": "69420"
                    },
                    body: JSON.stringify({
                        text: text,
                        plant_name: p.name,
                        day: getDays(p),
                        weather: currentWeatherInfo
                    })
                });
                const aiData = await aiRes.json();
                document.getElementById("aiReply").innerText = "🌱 AI 回覆：" + aiData.reply;
            }
        } catch(e) {
            document.getElementById("aiReply").innerText = "⚠️ 伺服器未連線";
        }

        p.diary.push(newEntry);
        saveData();
        updateDetailView();
        
        // 【修改重點】：拿掉自動關閉的倒數計時！
        // 我們只要在背景偷偷清空剛才輸入的文字和照片就好，讓彈窗乖乖開著
        document.getElementById("diaryText").value = "";
        fileInput.value = "";
    };

    if(file) {
        let reader = new FileReader();
        reader.onload = () => doSave(reader.result);
        reader.readAsDataURL(file);
    } else {
        doSave();
    }
}

function getDays(p){
  let diff = Math.floor((new Date() - new Date(p.startDate))/(1000*60*60*24));
  return diff + p.baseDay + 1;
}

function generateAI(day){
  return day <= 3 ? "🌱 剛開始，充滿希望！" : "🌿 穩定成長中，繼續加油！";
}

// --- 歷史紀錄 ---
function loadHistory(){
    let date = document.getElementById("historyDate").value;
    let list = document.getElementById("historyList");
    list.innerHTML = "";

    // 檢查：如果還沒選植物就跳出
    if (currentPlant === null) return;
    
    let p = plants[currentPlant]; // 只抓目前這盆植物
    let currentPlantName = p.name;

    // 只針對這盆植物的日記陣列跑迴圈
    p.diary.forEach((d, diaryIdx) => {
        if (d.date.split("T")[0] === date) {
            let div = document.createElement("div");
            div.style.padding = "10px";
            div.style.borderBottom = "1px solid #eee";
            div.style.textAlign = "left";
            
            // 抓取文字內容 (相容妳可能用的不同欄位名稱)
            let content = d.text || d.record || "無文字內容";

            div.innerHTML = `
                <div style="margin-bottom:5px;">
                    <b style="color:#2e7d32;">Day ${d.day}</b>
                    <button onclick="deleteDiary(${currentPlant}, ${diaryIdx})" style="float:right; border:none; background:none; cursor:pointer;">🗑️</button>
                </div>
                <div style="margin:10px 0;">${content}</div>
                <small style="color:#888;">${d.weather}</small>
                ${d.img ? `<br><img src="${d.img}" style="max-width:100%; border-radius:10px; margin-top:10px;">` : ''}
            `;
            list.appendChild(div);
        }
    });

    // 如果這天沒紀錄，顯示正確的植物名稱
    if(!list.innerHTML) {
        list.innerHTML = `<p style="color:#999; padding:20px; text-align:center;">${currentPlantName} 在這天沒有紀錄</p>`;
    }
}

function deleteDiary(pIdx, dIdx){
  if(confirm("確定刪除這條日記嗎？")){
    plants[pIdx].diary.splice(dIdx, 1);
    saveData(); renderPlants(); loadHistory();
  }
}

window.onload=function(){
  document.getElementById("loginPage").classList.remove("hidden");
};

// 新增這個函數，確保打開歷史紀錄時資料是新的
function openHistoryView() {
    // 1. 自動設定日期選擇器為「今天」 (ISO 格式 yyyy-mm-dd)
    const today = new Date().toLocaleDateString('en-CA'); 
    document.getElementById("historyDate").value = today;
    
    // 2. 先執行一次讀取資料，這樣一打開就不會看到上一個植物的名字
    loadHistory();
    
    // 3. 最後才打開彈窗
    openModal('historyModal');
}
