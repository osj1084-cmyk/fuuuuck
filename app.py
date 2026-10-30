import streamlit as st

st.set_page_config(page_title="장보기 알림메모", page_icon="🛒", layout="centered")

CATS = {"🥬 야채": "야채", "🍎 과일": "과일", "🥩 육류": "육류", "🐟 수산": "수산",
        "🥛 유제품": "유제품", "🍞 가공/기타": "기타"}
IMP = {1: "🟢1 있으면", 2: "🟡2 필요", 3: "🔴3 필수"}

# ---------- 상태 ----------
S = st.session_state
S.setdefault("memo", [])      # {id,cat,name,imp,limit}
S.setdefault("cart", [])      # {name,cat,price,qty}
S.setdefault("nid", 1)

# ---------- 컴팩트 CSS ----------
st.markdown("""
<style>
.block-container{padding:.5rem .6rem 0 .6rem;max-width:520px}
header,footer,#MainMenu{visibility:hidden;height:0}
div[data-testid="stVerticalBlock"]{gap:.3rem}
.stButton>button{padding:.1rem .4rem;min-height:1.9rem;width:100%}
.stTextInput input,.stNumberInput input{padding:.2rem .4rem;min-height:1.9rem}
div[data-testid="stTabs"] button{padding:.2rem .5rem}
.tot{background:#e8f5e9;border-radius:8px;padding:.3rem .6rem;font-size:.95rem;
display:flex;justify-content:space-between}
.small{font-size:.8rem;color:#666}
</style>""", unsafe_allow_html=True)

cart_total = sum(c["price"] * c["qty"] for c in S.cart)
left = len(S.memo)
st.markdown(
    f"<div class='tot'><b>🛒 담은 금액 {cart_total:,}원</b>"
    f"<span>메모 {left}개 · 카트 {len(S.cart)}개</span></div>",
    unsafe_allow_html=True)

t_memo, t_add, t_cart = st.tabs([f"📝 메모({left})", "➕ 추가", f"🧺 카트({len(S.cart)})"])

# ---------- 추가 ----------
with t_add:
    cat = st.radio("카테고리", list(CATS), horizontal=True, label_visibility="collapsed")
    name = st.text_input("상품명", placeholder="예: 대파 1단, 청송사과", label_visibility="collapsed")
    c1, c2 = st.columns(2)
    imp = c1.radio("중요도", [1, 2, 3], format_func=lambda x: IMP[x], index=1, horizontal=False)
    limit = c2.number_input("이 가격 넘으면 패스(원, 0=무제한)", 0, 1000000, 0, 500)
    if st.button("메모에 추가", type="primary"):
        if name.strip():
            S.memo.append({"id": S.nid, "cat": CATS[cat], "name": name.strip(),
                           "imp": imp, "limit": int(limit)})
            S.nid += 1
            st.rerun()
        else:
            st.warning("상품명을 입력하세요")

# ---------- 메모 (중요도 높은 순, 필터) ----------
with t_memo:
    f1, f2 = st.columns([3, 2])
    fcat = f1.selectbox("분류", ["전체"] + list(dict.fromkeys(CATS.values())),
                        label_visibility="collapsed")
    only = f2.toggle("⭐필수만", help="중요도 3만 보기")
    items = [m for m in S.memo
             if (fcat == "전체" or m["cat"] == fcat) and (not only or m["imp"] == 3)]
    items.sort(key=lambda m: -m["imp"])
    if not items:
        st.caption("메모가 없어요. ➕추가 탭에서 등록하세요.")
    with st.container(height=330, border=False):
        for m in items:
            a, b, c = st.columns([5, 2, 1.3])
            lim = f" · ≤{m['limit']:,}원" if m["limit"] else ""
            a.markdown(f"{IMP[m['imp']][:2]} **{m['name']}**  \n"
                       f"<span class='small'>{m['cat']}{lim}</span>", unsafe_allow_html=True)
            if b.button("🛒담기", key=f"p{m['id']}"):
                S.picking = m["id"]
            if c.button("✖", key=f"d{m['id']}"):
                S.memo = [x for x in S.memo if x["id"] != m["id"]]
                st.rerun()

    # 담기 입력 (가격·수량 필수)
    pid = S.get("picking")
    m = next((x for x in S.memo if x["id"] == pid), None)
    if m:
        st.markdown(f"**{m['name']}** 담기")
        p1, p2, p3 = st.columns([3, 2, 2])
        price = p1.number_input("단가(원)", 0, 10000000, 0, 100, key="pr")
        qty = p2.number_input("수량", 1, 99, 1, key="qt")
        p3.write("")
        if p3.button("확인", type="primary"):
            if m["limit"] and price > m["limit"]:
                S.warn = f"⚠️ 상한 {m['limit']:,}원 초과! 그래도 담으려면 다시 확인"
                S.over = True
            if S.get("over") and S.get("warn") and price > m["limit"] and not S.get("ok"):
                S.ok = True
                st.warning(S.warn)
            else:
                S.cart.append({"name": m["name"], "cat": m["cat"], "price": int(price), "qty": int(qty)})
                S.memo = [x for x in S.memo if x["id"] != pid]
                for k in ("picking", "warn", "over", "ok"):
                    S.pop(k, None)
                st.rerun()
        if m["limit"]:
            st.caption(f"💡 {m['limit']:,}원 넘으면 패스! (초과 시 한 번 더 확인)")

# ---------- 카트 ----------
with t_cart:
    if not S.cart:
        st.caption("아직 담은 물건이 없어요.")
    with st.container(height=300, border=False):
        for i, c in enumerate(S.cart):
            a, b = st.columns([6, 1.3])
            a.markdown(f"**{c['name']}** <span class='small'>{c['cat']}</span>  \n"
                       f"{c['price']:,}원 × {c['qty']} = **{c['price']*c['qty']:,}원**",
                       unsafe_allow_html=True)
            if b.button("↩", key=f"r{i}", help="카트에서 빼기"):
                S.cart.pop(i)
                st.rerun()
    st.markdown(f"**합계: {cart_total:,}원**")
    if S.cart and st.button("🧹 장보기 종료(전체 초기화)"):
        S.cart = []
        S.memo = []
        st.rerun()
