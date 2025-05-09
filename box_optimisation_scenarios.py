import streamlit as st
from itertools import permutations, combinations
import numpy as np
import copy
import math
import plotly.graph_objects as go

# Define box types
boxes = {
    "box_small": {
        "dimensions": (30, 30, 30),
        "max_weight": 2500,
        "box_cost": 1,
        "shipping_cost": 4
    },
    "box_large_high_quality": {
        "dimensions": (50, 50, 50),
        "max_weight": 5000,
        "box_cost": 2,
        "shipping_cost": 6
    },
    "box_large_low_quality": {
        "dimensions": (50, 50, 50),
        "max_weight": 3000,
        "box_cost": 2,
        "shipping_cost": 4
    }
}

# Define products with colors
products = {
    "product_a": {"dimensions": (30, 30, 15), "weight": 1000, "color": "yellow"},
    "product_b": {"dimensions": (30, 30, 10), "weight": 1000, "color": "green"},
    "product_c": {"dimensions": (50, 50, 25), "weight": 2000, "color": "blue"},
    "product_d": {"dimensions": (50, 50, 10), "weight": 1500, "color": "pink"},
    "product_e": {"dimensions": (10, 30, 10), "weight": 100, "color": "blue"},
    "product_f": {"dimensions": (6, 6, 6), "weight": 10, "color": "green"},
    "product_g": {"dimensions": (10, 10, 10), "weight": 1, "color": "yellow"},
    "product_h": {"dimensions": (2, 2, 2), "weight": 1, "color": "blue"},
    "product_i": {"dimensions": (6, 6, 6), "weight": 200, "color": "pink"},
    "product_j": {"dimensions": (30, 30, 15), "weight": 1500, "color": "blue"},
}

# Define orders
orders = {
    "order_1": {"product_a": 2},
    "order_2": {"product_b": 3},
    "order_3": {"product_c": 2},
    "order_4": {"product_d": 3},
    "order_5": {"product_d": 5},
    "order_6": {"product_b": 2, "product_e": 3},
    "order_7": {"product_b": 2, "product_e": 4, "product_f": 1, "product_h": 2},
    "order_8": {"product_b": 2, "product_e": 4, "product_i": 1, "product_h": 2},
    "order_9": {"product_a": 6},
    "order_10": {"product_j": 6}
}

def can_fit(box_dim, product_dims):
    for perm in permutations(product_dims):
        if all(p <= b for p, b in zip(perm, box_dim)):
            return True
    return False

def expand_order(order):
    items = []
    for product, amount in order.items():
        items.extend([product] * amount)
    return items

def pack_items_into_box(box_name, items):
    box = boxes[box_name]
    box_dim = box['dimensions']
    max_weight = box['max_weight']
    packed_items = []
    current_weight = 0

    for item in items:
        prod = products[item]
        if can_fit(box_dim, prod['dimensions']) and current_weight + prod['weight'] <= max_weight:
            packed_items.append(item)
            current_weight += prod['weight']

    return packed_items

def all_packings(order_items):
    min_total_cost = float('inf')
    best_packing = []

    def helper(remaining_items, current_boxes):
        nonlocal min_total_cost, best_packing
        if not remaining_items:
            total_cost = sum(boxes[b[0]]['box_cost'] + boxes[b[0]]['shipping_cost'] for b in current_boxes)
            if total_cost < min_total_cost:
                min_total_cost = total_cost
                best_packing = copy.deepcopy(current_boxes)
            return

        for box_name in boxes:
            packed_items = pack_items_into_box(box_name, remaining_items)
            if packed_items:
                new_remaining = remaining_items.copy()
                for p in packed_items:
                    new_remaining.remove(p)
                current_boxes.append((box_name, packed_items))
                helper(new_remaining, current_boxes)
                current_boxes.pop()

    helper(order_items, [])
    return best_packing

def visualize_packing(packing_result):
    figures = []
    for box_index, (box_name, items) in enumerate(packing_result):
        box = boxes[box_name]
        box_dim = box["dimensions"]
        fig = go.Figure()
        fig.update_layout(
            title=f"Box {box_index + 1}: {box_name}",
            scene=dict(
                xaxis=dict(title="Length", range=[0, box_dim[2]], backgroundcolor="saddlebrown", showspikes=False),
                yaxis=dict(title="Width", range=[0, box_dim[1]], backgroundcolor="saddlebrown", showspikes=False),
                zaxis=dict(title="Height", range=[0, box_dim[0]], backgroundcolor="saddlebrown", showspikes=False),
                aspectratio=dict(x=box_dim[2]/50, y=box_dim[1]/50, z=box_dim[0]/50),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor="linen",
            plot_bgcolor="linen"
        )

        offset_x = offset_y = offset_z = 0
        step = 0
        for item in items:
            prod = products[item]
            dims = sorted(prod["dimensions"], reverse=True)
            color = prod.get("color", "lightgrey")
            hover_text = f"<b>{item}</b><br>Dimensions: {prod['dimensions']}<br>Weight: {prod['weight']}g"
            fig.add_trace(go.Mesh3d(
                x=[offset_x, offset_x+dims[2], offset_x+dims[2], offset_x, offset_x, offset_x+dims[2], offset_x+dims[2], offset_x],
                y=[offset_y, offset_y, offset_y+dims[1], offset_y+dims[1], offset_y, offset_y, offset_y+dims[1], offset_y+dims[1]],
                z=[offset_z, offset_z, offset_z, offset_z, offset_z+dims[0], offset_z+dims[0], offset_z+dims[0], offset_z+dims[0]],
                i=[0, 0, 0, 1, 1, 2, 2, 3, 4, 5, 6, 7],
                j=[1, 2, 4, 2, 5, 3, 6, 0, 5, 6, 7, 4],
                k=[2, 3, 5, 3, 6, 0, 7, 1, 6, 7, 4, 5],
                opacity=0.5,
                color=color,
                hovertext=hover_text,
                hoverinfo="text",
                name=item,
                showscale=False
            ))
            offset_x += dims[2]
            step += 1

        figures.append(fig)
    return figures

# Streamlit UI
st.title("Box Packing Optimizer")

order_input = st.selectbox("Select Order", list(orders.keys()))

if st.button("Optimize Packing"):
    if not order_input:
        st.warning("Please select an order.")
    else:
        order_items = expand_order(orders[order_input])
        packing_result = all_packings(order_items)
        total_cost = 0
        for i, (box_name, items) in enumerate(packing_result, 1):
            box = boxes[box_name]
            cost = box['box_cost'] + box['shipping_cost']
            total_cost += cost
            st.subheader(f"Box {i}: {box_name}")
            st.write(f"Contains: {', '.join(items)}")
            st.write(f"Cost: {cost} Euro")

        st.success(f"Total Cost: {total_cost} Euro")

        st.subheader("Packing Visualizations")
        figures = visualize_packing(packing_result)
        for fig in figures:
            st.plotly_chart(fig)
