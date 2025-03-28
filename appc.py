import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# ============================
# 기본 설정 및 스타일
# ============================
st.set_page_config(layout="wide", page_title="스마트블럭 이미지 생성기")

st.markdown("""
    <style>
    .main { background-color: #f5f6fa; }
    .stTextInput>div>div>input {
        background-color: #ffffff !important;
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 6px;
    }
    .stButton button, .stDownloadButton button {
        background-color: #06C755;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.5em 1em;
    }
    </style>
""", unsafe_allow_html=True)

# ============================
# 한글 폰트 설정 (마루부리)
# ============================
FONT_PATH = "./MaruBuri-Bold.ttf"

def load_font(size):
    return ImageFont.truetype(FONT_PATH, size)

def add_rounded_corners(im, radius):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    im.putalpha(alpha)
    return im

# ============================
# 세션 상태 초기화
# ============================
if "image_list" not in st.session_state:
    st.session_state["image_list"] = []

# ============================
# 입력 영역
# ============================
st.title("🧩 스마트블럭 노출 이미지 생성기")

col1, col2 = st.columns([1, 2])
with col1:
    branch_name = st.text_input("📌 지점명", "부산광안점")
with col2:
    sub_title = st.text_input("📝 부제목", "대표 키워드 상위 노출 & 스마트블럭 노출 현황")

cards = []
st.subheader("📦 카드 제목 + 이미지 입력")
for i in range(4):
    with st.expander(f"카드 {i+1} 입력"):
        keyword = st.text_input("카드 제목 (회색 상자 안에 나올 내용)", key=f"kw{i}")
        image = st.file_uploader("썸네일 이미지 (드래그 앤 드롭)", type=["png", "jpg"], key=f"img{i}")
        cards.append((keyword, image))

# ============================
# 이미지 생성 버튼
# ============================
if st.button("✨ 이미지 생성하기"):
    canvas = Image.new("RGB", (1400, 1000), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    title_font = load_font(52)
    subtitle_font = load_font(28)
    content_font = load_font(22)

    # 상단 타이틀 + 오른쪽 부제목
    draw.rounded_rectangle([50, 30, 1350, 150], radius=10, fill="#E5CDB6")
    draw.text((100, 65), branch_name, font=title_font, fill="#1A1A1A")
    draw.text((730, 95), sub_title, font=subtitle_font, fill="#1A1A1A")

    # 카드 위치
    positions = [(50, 160), (720, 160), (50, 560), (720, 560)]

    for i, (keyword, image) in enumerate(cards):
        x, y = positions[i]
        draw.rounded_rectangle([x, y, x+630, y+390], radius=10, fill="#FFFFFF", outline="#D0D0D0")
        draw.rounded_rectangle([x+10, y+10, x+620, y+50], radius=10, fill="#E5CDB6")
        draw.text((x+22, y+20), keyword or "제목 없음", font=content_font, fill="#000000")

        if image:
            uploaded = Image.open(image).convert("RGB")
            resized = uploaded.resize((610, 320))
            rounded = add_rounded_corners(resized, 10)
            img_x = x + 10
            img_y = y + 60
            canvas.paste(rounded, (img_x, img_y), rounded)

    # 이미지 세션에 저장
    st.session_state.image_list.append(canvas.copy())

    # 출력 및 다운로드
    st.image(canvas, caption="🖼️ 생성된 이미지 미리보기")
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    st.download_button("📥 이미지 다운로드", data=buf.getvalue(), file_name="smartblock_result.png", mime="image/png")

# ============================
# 저장된 이미지 리스트 및 다운로드
# ============================
st.subheader("🖼️ 썸네일 미리보기 갤러리")

if st.session_state.image_list:
    cols = st.columns(2)
    for idx, img in enumerate(st.session_state.image_list):
        with cols[idx % 2]:
            st.image(img.resize((700, 500)), caption=f"{branch_name}_스마트블럭_{idx + 1}")

            # 자동 파일명 생성
            base_filename = f"{branch_name}_스마트블럭_{idx + 1}"

            # PNG 다운로드
            img_buf = io.BytesIO()
            img.save(img_buf, format="PNG")
            st.download_button(
                label="📥 PNG 다운로드",
                data=img_buf.getvalue(),
                file_name=f"{base_filename}.png",
                mime="image/png",
                key=f"download_png_{idx}"
            )

            # PDF 다운로드
            pdf_buf = io.BytesIO()
            img_rgb = img.convert("RGB")
            img_rgb.save(pdf_buf, format="PDF")
            st.download_button(
                label="📄 PDF 다운로드",
                data=pdf_buf.getvalue(),
                file_name=f"{base_filename}.pdf",
                mime="application/pdf",
                key=f"download_pdf_{idx}"
            )

    # 병합 PDF 다운로드
    st.subheader("📚 전체 병합 PDF 다운로드")
    merged_pdf_buf = io.BytesIO()
    img_list = [img.convert("RGB") for img in st.session_state.image_list]
    img_list[0].save(
        merged_pdf_buf,
        format="PDF",
        save_all=True,
        append_images=img_list[1:]
    )
    st.download_button(
        label="📄 전체 PDF 한 파일로 다운로드",
        data=merged_pdf_buf.getvalue(),
        file_name=f"{branch_name}_스마트블럭_합본.pdf",
        mime="application/pdf"
    )
