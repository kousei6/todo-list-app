import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid

# タスクデータの初期化
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# タスクの追加
def add_task():
    if task_name:
        st.session_state.tasks.append({
            "id": str(uuid.uuid4()),
            "name": task_name,
            "deadline": deadline,
            "memo": memo,
            "category": category,
            "completed": False,
            "created": datetime.now(),
            "repeat": repeat
        })

        # 繰り返しタスクの自動生成（1週間分）
        if repeat != "なし":
            for i in range(1, 8):
                if repeat == "毎日":
                    next_date = deadline + timedelta(days=i)
                elif repeat == "毎週":
                    next_date = deadline + timedelta(weeks=i)
                else:
                    break

                st.session_state.tasks.append({
                    "id": str(uuid.uuid4()),
                    "name": f"{task_name} ({i+1})",
                    "deadline": next_date,
                    "memo": memo,
                    "category": category,
                    "completed": False,
                    "created": datetime.now(),
                    "repeat": repeat
                })

# タスクの編集
def edit_task(task_id, name, deadline, memo, category, repeat):
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            task["name"] = name
            task["deadline"] = deadline
            task["memo"] = memo
            task["category"] = category
            task["repeat"] = repeat

# タスクの削除
def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]

# 保存
def export_to_excel():
    df = pd.DataFrame(st.session_state.tasks)
    df.to_excel("todo_export.xlsx", index=False)
    st.success("Excelに保存しました (todo_export.xlsx)")

# 完了率のグラフ
def show_progress_graph():
    total = len(st.session_state.tasks)
    done = sum(task["completed"] for task in st.session_state.tasks)
    if total == 0:
        return



    # 円グラフ
    ax[0].pie([done, total - done], labels=["完了", "未完了"], autopct="%1.1f%%", colors=["#4CAF50", "#FF6F61"])
    ax[0].set_title("完了率（円グラフ）")

    # 棒グラフ
    ax[1].bar(["完了", "未完了"], [done, total - done], color=["#4CAF50", "#FF6F61"])
    ax[1].set_title("完了タスク数（棒グラフ）")

    st.pyplot(fig)

# --- UI ---
st.title("ToDoリストアプリ")

st.subheader("新しいタスクを追加")
task_name = st.text_input("タスク名")
deadline = st.date_input("締切", value=datetime.now().date())
memo = st.text_area("メモ", height=68)
category = st.selectbox("カテゴリ", ["学校", "バイト", "趣味", "その他"])
repeat = st.selectbox("繰り返し", ["なし", "毎日", "毎週"])
st.button("追加", on_click=add_task)

st.divider()

# 並び替え・フィルター
sort_by = st.selectbox("並び替え", ["追加順", "締切順"])
filter_by = st.selectbox("表示フィルター", ["すべて", "完了", "未完了"])
category_filter = st.selectbox("カテゴリフィルター", ["すべて"] + list(set(t["category"] for t in st.session_state.tasks)))

# 並び替え
if sort_by == "締切順":
    tasks = sorted(st.session_state.tasks, key=lambda x: x["deadline"])
else:
    tasks = st.session_state.tasks

# フィルター
if filter_by != "すべて":
    tasks = [t for t in tasks if t["completed"] == (filter_by == "完了")]

if category_filter != "すべて":
    tasks = [t for t in tasks if t["category"] == category_filter]

# タスク表示
st.subheader("タスクリスト")
for task in tasks:
    with st.expander(f"{task['name']}（{task['category']}）", expanded=False):
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            task["completed"] = st.checkbox("完了", value=task["completed"], key=task["id"])
        with col2:
            st.write(f"締切: {task['deadline']}")
            st.write(f"メモ: {task['memo']}")
            # 編集
            with st.container():
                st.markdown("編集")
                new_name = st.text_input("タスク名", value=task["name"], key=task["id"]+"_edit")
                new_deadline = st.date_input("締切", value=task["deadline"], key=task["id"]+"_date")
                new_memo = st.text_area("メモ", value=task["memo"], height=80, key=task["id"]+"_memo")
                new_category = st.selectbox("カテゴリ", ["学校", "バイト", "趣味", "その他"], index=["学校", "バイト", "趣味", "その他"].index(task["category"]), key=task["id"]+"_cat")
                new_repeat = st.selectbox("繰り返し", ["なし", "毎日", "毎週"], index=["なし", "毎日", "毎週"].index(task["repeat"]), key=task["id"]+"_rep")
                if st.button("保存", key=task["id"]+"_save"):
                    edit_task(task["id"], new_name, new_deadline, new_memo, new_category, new_repeat)
                    st.success("タスクを更新しました。")
            if st.button("削除", key=task["id"]+"_delete"):
                delete_task(task["id"])
                st.warning("タスクを削除しました。")

st.divider()

# グラフと保存
st.subheader("完了率グラフ")


st.subheader("タスクデータの保存")
st.button("Excelとして保存", on_click=export_to_excel)
