#!/usr/bin/env python3

def test_column_major_distribution():
    """Test the column-major distribution logic"""
    
    # Simulate the field distribution logic
    def distribute_fields_column_major(total_fields, num_columns):
        """Distribute fields into columns using column-major order"""
        fields_per_column = (total_fields + num_columns - 1) // num_columns  # Ceiling division
        
        column_assignments = []
        for i in range(total_fields):
            column_index = i // fields_per_column
            # Ensure we don't exceed the number of columns
            if column_index >= num_columns:
                column_index = num_columns - 1
            column_assignments.append(column_index)
        
        return column_assignments, fields_per_column
    
    def distribute_fields_round_robin(total_fields, num_columns):
        """Distribute fields using round-robin (row-major) order"""
        column_assignments = []
        for i in range(total_fields):
            column_index = i % num_columns
            column_assignments.append(column_index)
        
        return column_assignments
    
    # Test with different numbers of fields
    test_cases = [8, 9, 10, 11, 12, 15]
    num_columns = 3
    
    for total_fields in test_cases:
        print(f"\n=== Testing with {total_fields} fields ===")
        
        # Column-major distribution
        col_major, fields_per_col = distribute_fields_column_major(total_fields, num_columns)
        print(f"Column-major (fields_per_column={fields_per_col}): {col_major}")
        
        # Round-robin distribution
        round_robin = distribute_fields_round_robin(total_fields, num_columns)
        print(f"Round-robin: {round_robin}")
        
        # Show how fields are distributed
        print("Column-major distribution:")
        for col in range(num_columns):
            fields_in_col = [i for i, c in enumerate(col_major) if c == col]
            print(f"  Column {col}: fields {fields_in_col}")
        
        print("Round-robin distribution:")
        for col in range(num_columns):
            fields_in_col = [i for i, c in enumerate(round_robin) if c == col]
            print(f"  Column {col}: fields {fields_in_col}")

if __name__ == "__main__":
    test_column_major_distribution()
