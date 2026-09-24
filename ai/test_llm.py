from analyzer import generate_analysis 

sample_summary = """
Dataset Overview:
- Total Rows: 100
- Total Columns: 5
- Missing Values: 8
- Duplicate Rows: 2

Column Information:
- name: text
- age: numerical
- salary: numerical
"""

result = generate_analysis(sample_summary)

print(result)