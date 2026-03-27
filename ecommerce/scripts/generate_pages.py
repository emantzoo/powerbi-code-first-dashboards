import json, os, hashlib, shutil

BASE = r"C:\Users\emant\Downloads\powerBI_recipes\Ecommerce\ECommerceDashboard.Report\definition\pages"
SV = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json"
SP = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SM = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"

def uid(s): return hashlib.md5(s.encode()).hexdigest()[:20]
def mf(t,m): return {"field":{"Measure":{"Expression":{"SourceRef":{"Entity":t}},"Property":m}},"queryRef":f"{t}.{m}","nativeQueryRef":m}
def cf(t,c): return {"field":{"Column":{"Expression":{"SourceRef":{"Entity":t}},"Property":c}},"queryRef":f"{t}.{c}","nativeQueryRef":c}

def mv(name,x,y,w,h,vt,qs):
    return {"$schema":SV,"name":uid(name),"position":{"x":x,"y":y,"z":1000,"height":h,"width":w,"tabOrder":0},
            "visual":{"visualType":vt,"query":{"queryState":qs},"drillFilterOtherVisuals":True}}

def card(n,x,y,w,h,t,m): return mv(n,x,y,w,h,"cardVisual",{"Data":{"projections":[mf(t,m)]}})
def slicer(n,x,y,w,h,t,c): return mv(n,x,y,w,h,"slicer",{"Values":{"projections":[cf(t,c)]}})
def bar(n,x,y,w,h,ct,cc,vt,vm): return mv(n,x,y,w,h,"clusteredBarChart",{"Category":{"projections":[cf(ct,cc)]},"Y":{"projections":[mf(vt,vm)]}})
def line(n,x,y,w,h,ct,cc,vt,vm,vt2=None,vm2=None):
    qs={"Category":{"projections":[cf(ct,cc)]},"Y":{"projections":[mf(vt,vm)]}}
    if vt2: qs["Y"]["projections"].append(mf(vt2,vm2))
    return mv(n,x,y,w,h,"lineChart",qs)
def area(n,x,y,w,h,ct,cc,vt,vm): return mv(n,x,y,w,h,"areaChart",{"Category":{"projections":[cf(ct,cc)]},"Y":{"projections":[mf(vt,vm)]}})
def donut(n,x,y,w,h,ct,cc,vt,vm): return mv(n,x,y,w,h,"donutChart",{"Category":{"projections":[cf(ct,cc)]},"Y":{"projections":[mf(vt,vm)]}})
def table(n,x,y,w,h,fl):
    return mv(n,x,y,w,h,"tableEx",{"Values":{"projections":[mf(t,c) if m else cf(t,c) for t,c,m in fl]}})
def matrix(n,x,y,w,h,rf,colf,vf):
    return mv(n,x,y,w,h,"pivotTable",{"Rows":{"projections":[cf(t,c) for t,c in rf]},"Columns":{"projections":[cf(t,c) for t,c in colf]},"Values":{"projections":[mf(t,m) for t,m in vf]}})

def write_visual(pd,v):
    d=os.path.join(pd,"visuals",v["name"]); os.makedirs(d,exist_ok=True)
    with open(os.path.join(d,"visual.json"),"w",encoding="utf-8") as f: json.dump(v,f,indent=2,ensure_ascii=False)
def write_page(pid,dn,vs):
    pd=os.path.join(BASE,pid); os.makedirs(os.path.join(pd,"visuals"),exist_ok=True)
    with open(os.path.join(pd,"page.json"),"w",encoding="utf-8") as f:
        json.dump({"$schema":SP,"name":pid,"displayName":dn,"displayOption":"FitToPage","height":720,"width":1280},f,indent=2)
    for v in vs: write_visual(pd,v)

# PAGE 1: Executive Overview
p1=uid("ec_p1_overview")
v1=[
    card("ec1_rev",20,10,295,110,"_Measures","Total Revenue"),
    card("ec1_profit",330,10,295,110,"_Measures","Total Profit"),
    card("ec1_margin",640,10,295,110,"_Measures","Profit Margin"),
    card("ec1_orders",950,10,295,110,"_Measures","Total Orders"),
    bar("ec1_cat",20,140,400,280,"DimProduct","category","_Measures","Total Revenue"),
    line("ec1_trend",440,140,400,280,"Calendar","Year_Month","_Measures","Total Revenue"),
    donut("ec1_channel",860,140,380,280,"DimStore","channel","_Measures","Total Revenue"),
    area("ec1_profit_area",20,440,600,260,"Calendar","Year_Month","_Measures","Total Profit"),
    slicer("ec1_year",640,440,200,260,"Calendar","Year"),
    bar("ec1_region",860,440,380,260,"DimStore","region","_Measures","Total Orders"),
]

# PAGE 2: Product Performance
p2=uid("ec_p2_product")
v2=[
    card("ec2_rev",20,10,235,110,"_Measures","Total Revenue"),
    card("ec2_aov",270,10,235,110,"_Measures","Avg Order Value"),
    card("ec2_qty",520,10,235,110,"_Measures","Total Quantity"),
    card("ec2_rr",770,10,235,110,"_Measures","Return Rate"),
    slicer("ec2_cat",1020,10,230,110,"DimProduct","category"),
    bar("ec2_subcat",20,140,610,280,"DimProduct","subcategory","_Measures","Total Revenue"),
    bar("ec2_brand",650,140,600,280,"DimProduct","brand","_Measures","Total Profit"),
    table("ec2_tbl",20,440,1230,260,[
        ("DimProduct","category",False),("DimProduct","subcategory",False),("DimProduct","brand",False),
        ("_Measures","Total Revenue",True),("_Measures","Total Profit",True),("_Measures","Profit Margin",True),
        ("_Measures","Total Quantity",True),("_Measures","Return Rate",True)]),
]

# PAGE 3: Customer & Trends
p3=uid("ec_p3_customer")
v3=[
    card("ec3_cust",20,10,295,110,"_Measures","Total Customers"),
    card("ec3_yoy",330,10,295,110,"_Measures","Revenue YoY Growth"),
    card("ec3_ytd",640,10,295,110,"_Measures","Revenue YTD"),
    card("ec3_l12m",950,10,295,110,"_Measures","Revenue L12M"),
    line("ec3_trend",20,140,610,280,"Calendar","Year_Month","_Measures","Total Revenue","_Measures","Revenue PY"),
    donut("ec3_seg",650,140,290,280,"DimCustomer","segment","_Measures","Total Revenue"),
    bar("ec3_country",960,140,290,280,"DimCustomer","country","_Measures","Total Customers"),
    matrix("ec3_matrix",20,440,1230,260,
        [("DimCustomer","country")],[("Calendar","Year")],
        [("_Measures","Total Revenue"),("_Measures","Total Orders")]),
]

# PAGE 4: Returns Analysis
p4=uid("ec_p4_returns")
v4=[
    card("ec4_returns",20,10,295,110,"_Measures","Total Returns"),
    card("ec4_refunds",330,10,295,110,"_Measures","Total Refunds"),
    card("ec4_rr",640,10,295,110,"_Measures","Return Rate"),
    card("ec4_net",950,10,295,110,"_Measures","Net Revenue"),
    bar("ec4_reason",20,140,400,280,"FactReturns","reason_code","_Measures","Total Returns"),
    line("ec4_trend",440,140,400,280,"Calendar","Year_Month","_Measures","Returns by Date"),
    donut("ec4_cat",860,140,380,280,"DimProduct","category","_Measures","Total Returns"),
    table("ec4_tbl",20,440,1230,260,[
        ("FactReturns","reason_code",False),("_Measures","Total Returns",True),
        ("_Measures","Total Refunds",True),("_Measures","Return Rate",True)]),
]

# Remove old page
old=os.path.join(BASE,"490f2ef98a69f04305b5")
if os.path.exists(old): shutil.rmtree(old)

write_page(p1,"Executive Overview",v1)
write_page(p2,"Product Performance",v2)
write_page(p3,"Customer & Trends",v3)
write_page(p4,"Returns Analysis",v4)

with open(os.path.join(BASE,"pages.json"),"w",encoding="utf-8") as f:
    json.dump({"$schema":SM,"pageOrder":[p1,p2,p3,p4],"activePageName":p1},f,indent=2)

print(f"Page 1 (Executive Overview): {p1} - {len(v1)} visuals")
print(f"Page 2 (Product Performance): {p2} - {len(v2)} visuals")
print(f"Page 3 (Customer & Trends): {p3} - {len(v3)} visuals")
print(f"Page 4 (Returns Analysis): {p4} - {len(v4)} visuals")
print("Done!")
