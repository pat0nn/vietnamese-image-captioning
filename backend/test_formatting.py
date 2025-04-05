def format_caption(caption):
    # Remove underscores
    formatted = caption.replace('_', ' ')
    
    # Capitalize the first letter
    if formatted:
        formatted = formatted[0].upper() + formatted[1:]
    
    # Add period at the end if not present
    if formatted and not formatted.endswith(('.', '!', '?')):
        formatted += '.'
        
    return formatted

# Test cases
test_cases = [
    'có nhiều con thuyền đang xuất_hiện ở trên biển',
    'một người đàn_ông đang đứng trên bãi_biển',
    'chiếc xe_đạp màu đỏ đậu bên đường',
    'hai đứa trẻ đang chơi trong công_viên',
    'một con chó đang chạy trên bãi cỏ.'  # Already has period
]

print("Testing caption formatting:")
print("-" * 50)
for i, test in enumerate(test_cases):
    formatted = format_caption(test)
    print(f"Test {i+1}:")
    print(f"Original: {test}")
    print(f"Formatted: {formatted}")
    print("-" * 50)

print("Formatting complete!") 