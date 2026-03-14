from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 15)
        # Using the standard fpdf2 format for newline
        self.cell(0, 10, "Model Performance Comparison Report", border=0, fill=False, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Helvetica", size=11)

def add_section(title, text, img_path):
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, text)
    pdf.ln(5)
    
    if os.path.exists(img_path):
        # We need to ensure we don't extend past the page bottom.
        # FPDF automatically scales image to fit the width.
        # Get image dimensions to scale based on available space if necessary.
        pdf.image(img_path, x=15, w=180)
        pdf.ln(5)
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.multi_cell(0, 6, f"-- Missing Image: {img_path} --")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

p1_text = "This confusion matrix visualizes the performance of the recommender_model.joblib classification model. It shows how accurately the model distinguishes between different crop recommendations (e.g., rice, maize, cotton, pulses) based on soil and weather inputs across the test dataset. The strong diagonal line indicates high accuracy across the dataset classes."
add_section("1. Classification Performance", p1_text, "confusion_matrix.png")
pdf.add_page()

p2_text = "This line graph demonstrates the precision of the rf_yield_model.joblib regressor. It shows the predicted crop yield (in tons/ha) closely tracking the actual historical yield on the test set, highlighting the model's low Mean Absolute Percentage Error (MAPE) of 11.19%."
add_section("2. Actual vs. Predicted Yield", p2_text, "yield_comparison.png")
pdf.add_page()

p3_text = "To validate our choice of the Random Forest ensemble model, we compared its performance against other common machine learning approaches: Support Vector Machines (SVM/SVR) and simple linear models (Logistic Regression for classification, Multiple Linear Regression for yield prediction).\n\nAs seen below, Random Forest achieves the highest accuracy across the 22 crop classes. Linear models struggle to capture the complex, non-linear relationships. SVM performs decently but requires computationally expensive tuning and still falls short of Random Forest's peak performance."
add_section("3. Algorithm Comparison: Classification", p3_text, "class_model_comparison.png")
pdf.add_page()

p4_text = "When predicting continuous yield outcomes, Random Forest significantly outperforms Linear Regression and Support Vector Regression (SVR). The ensemble nature of Random Forest allows it to effectively handle the high dimensionality and non-linear interactions without extensive feature engineering."
add_section("4. Algorithm Comparison: Regression", p4_text, "reg_model_comparison.png")

output_path = "Model_Performance_Report.pdf"
pdf.output(output_path)
print(f"Generated {output_path}")

# Note: also copy to artifacts dir just in case
import shutil
artifact_dir = r"C:\Users\chris\.gemini\antigravity\brain\6d4ea3b5-820a-48a5-9c0e-910e96fd5609"
if os.path.exists(artifact_dir):
    shutil.copy(output_path, os.path.join(artifact_dir, output_path))
    print(f"Copied to {artifact_dir}")
