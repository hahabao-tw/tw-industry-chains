/* 由 build.py 自動產生；此為初始種子資料（太空衛星科技，ic=4100）
   公司格式：
     台灣公司  {n:"名稱", c:"代號", m:"上市|上櫃|興櫃", d:"官網域名(可空)"}
     外國企業  {n:"名稱", d:"官網域名"}
*/
window.CHAIN_DATA = {
  updated: "2026-07-10 (seed)",
  industries: [
    {
      ic: "4100",
      name: "太空衛星科技",
      layers: [
        {
          name: "上游 · 設備製造",
          segments: [
            { name: "零組件/材料", subs: [
              { name: "天線/射頻基頻", companies: [
                {n:"台達電",c:"2308",m:"上市",d:""},{n:"台揚",c:"2314",m:"上市",d:""},
                {n:"佳世達",c:"2352",m:"上市",d:""},{n:"明泰",c:"3380",m:"上市",d:""},
                {n:"同欣電",c:"6271",m:"上市",d:""},{n:"啟碁",c:"6285",m:"上市",d:""},
                {n:"穩懋",c:"3105",m:"上櫃",d:""},{n:"昇達科",c:"3491",m:"上櫃",d:""},
                {n:"新復興",c:"4909",m:"上櫃",d:""},{n:"宣德",c:"5457",m:"上櫃",d:""},
                {n:"崴寶",c:"7744",m:"上櫃",d:""},{n:"鐳洋科技",c:"6980",m:"興櫃",d:""},
                {n:"科建",c:"7886",m:"興櫃",d:""},
                {n:"亞德諾半導體",d:"analog.com"},{n:"Anokiwave",d:"anokiwave.com"},{n:"意法半導體",d:"st.com"}
              ]},
              { name: "太陽能板/電池", companies: [
                {n:"昇達科",c:"3491",m:"上櫃",d:""},{n:"新復興",c:"4909",m:"上櫃",d:""},
                {n:"宣德",c:"5457",m:"上櫃",d:""},{n:"崴寶",c:"7744",m:"上櫃",d:""},{n:"科建",c:"7886",m:"興櫃",d:""},
                {n:"Rocket Lab",d:"rocketlabusa.com"},{n:"Spectrolab",d:"spectrolab.com"}
              ]},
              { name: "感測器", companies: [
                {n:"原相",c:"3227",m:"上櫃",d:""},{n:"昇達科",c:"3491",m:"上櫃",d:""},
                {n:"新復興",c:"4909",m:"上櫃",d:""},{n:"宣德",c:"5457",m:"上櫃",d:""},
                {n:"崴寶",c:"7744",m:"上櫃",d:""},{n:"科建",c:"7886",m:"興櫃",d:""}
              ]},
              { name: "微電子", companies: [
                {n:"昇達科",c:"3491",m:"上櫃",d:""},{n:"新復興",c:"4909",m:"上櫃",d:""},
                {n:"宣德",c:"5457",m:"上櫃",d:""},{n:"崴寶",c:"7744",m:"上櫃",d:""},{n:"科建",c:"7886",m:"興櫃",d:""}
              ]},
              { name: "金屬/燃料", companies: [
                {n:"公準",c:"3178",m:"上櫃",d:""},{n:"昇達科",c:"3491",m:"上櫃",d:""},
                {n:"新復興",c:"4909",m:"上櫃",d:""},{n:"宣德",c:"5457",m:"上櫃",d:""},
                {n:"崴寶",c:"7744",m:"上櫃",d:""},{n:"益材科技",c:"7879",m:"興櫃",d:""},{n:"科建",c:"7886",m:"興櫃",d:""}
              ]}
            ]},
            { name: "次系統", subs: [
              { name: "酬載", companies: [
                {n:"鐳洋科技",c:"6980",m:"興櫃",d:""},
                {n:"空中巴士",d:"airbus.com"},{n:"L3Harris Technologies",d:"l3harris.com"},
                {n:"Northrop Grumman",d:"northropgrumman.com"},{n:"Thales Alenia Space",d:"thalesgroup.com"}
              ]},
              { name: "通訊", companies: [ {n:"鐳洋科技",c:"6980",m:"興櫃",d:""} ]},
              { name: "航電系統", companies: [ {n:"Aerojet Rocketdyne",d:"rocket.com"} ]}
            ]},
            { name: "整機", subs: [
              { name: "衛星", companies: [
                {n:"空中巴士",d:"airbus.com"},{n:"波音",d:"boeing.com"},
                {n:"洛克希德·馬丁",d:"lockheedmartin.com"},{n:"Thales Alenia Space",d:"thalesgroup.com"}
              ]},
              { name: "發射載具", companies: [
                {n:"Arca Space",d:"arcaspace.com"},{n:"Astra Space",d:"astra.com"}
              ]},
              { name: "太空船", companies: [
                {n:"Northrop Grumman",d:"northropgrumman.com"},{n:"SpaceX",d:"spacex.com"}
              ]},
              { name: "地面設備", companies: [
                {n:"Comtech",d:"comtechtel.com"},{n:"Gilat",d:"gilat.com"},{n:"ST Engineering iDirect",d:"idirect.net"}
              ]}
            ]}
          ]
        },
        {
          name: "中游 · 發射營運",
          segments: [
            { name: "發射服務", subs: [ { name: null, companies: [
              {n:"Arianespace",d:"arianespace.com"},{n:"Blue Origin",d:"blueorigin.com"},
              {n:"Northrop Grumman",d:"northropgrumman.com"},{n:"Rocket Lab",d:"rocketlabusa.com"},
              {n:"SpaceX",d:"spacex.com"},{n:"United Launch Alliance",d:"ulalaunch.com"},{n:"Virgin Orbit",d:"virginorbit.com"}
            ]}]},
            { name: "仲介服務", subs: [ { name: null, companies: [
              {n:"Nanoracks",d:"nanoracks.com"},{n:"SEOPS",d:"seopsllc.com"}
            ]}]},
            { name: "營運管理", subs: [ { name: null, companies: [
              {n:"Echostar",d:"echostar.com"},{n:"Eutelsat",d:"eutelsat.com"},{n:"Inmarsat",d:"inmarsat.com"},
              {n:"Kongsberg Satellite Services (K-SAT)",d:"ksat.no"},{n:"OneWeb",d:"oneweb.net"},
              {n:"俄羅斯航太",d:"roscosmos.ru"},{n:"Starlink",d:"starlink.com"},
              {n:"Swedish Space Corporation (SSC)",d:"sscspace.com"}
            ]}]}
          ]
        },
        {
          name: "下游 · 應用服務",
          segments: [
            { name: "通訊", subs: [ { name: null, companies: [
              {n:"凌群",c:"2453",m:"上市",d:""},
              {n:"Globalstar",d:"globalstar.com"},{n:"OneWeb",d:"oneweb.net"},
              {n:"Starlink",d:"starlink.com"},{n:"Viasat",d:"viasat.com"}
            ]}]},
            { name: "影像遙測", subs: [ { name: null, companies: [
              {n:"凌群",c:"2453",m:"上市",d:""},
              {n:"Maxar Technologies",d:"maxar.com"},{n:"Planet Labs",d:"planet.com"},{n:"Spire Global",d:"spire.com"}
            ]}]},
            { name: "導航定位", subs: [ { name: null, companies: [
              {n:"凌群",c:"2453",m:"上市",d:""},{n:"研勤",c:"3632",m:"上櫃",d:""},
              {n:"台灣國際航電",d:"garmin.com"},{n:"TomTom",d:"tomtom.com"}
            ]}]}
          ]
        }
      ]
    }
  ]
};
