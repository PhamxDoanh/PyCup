# CUP - NGÔN NGỮ LẬP TRÌNH CHO GIÁO DỤC VÀ PHÁT TRIỂN!

Đây là một triển khai về một ngôn ngữ lập trình thông dịch được viết và lấy cảm hứng từ [python](https://www.python.org/) với mục đích giáo dục, đào tạo đồng thời dùng cả trong phát triển khoa học máy tính, ... Dưới đây là cái nhìn tổng thể về ngôn ngữ này:

### I. Dự án này bao gồm:

- Lexer sử dụng biểu thức chính quy ([regex](https://en.wikipedia.org/wiki/Regular_expression))
- Parse sử dụng đệ quy từ trên xuống
- Interpreter hoạt dộng theo nguyên lí AST
- REPL hỗ trợ chạy lệnh trên cmd và tệp riêng lẻ


### II. Mục tiêu của Cup:

|Operators	|Description	|Example	|
|:---:		|:---:			|:---:		|
|Arithmetic	|`+, -, *, /, \, %, ^, |x|, x!`|`1 + 2, 8 - 8, 5!, |-12|, ...`|
|Assignment	|`=, :, x+, x- <br><br> +=, -=, *=, /=, \=, %=, ^=, &&=, ||=, ^^=`|`x = 10, name: 'Hxngxd', x+ (x = x + 1), x += y (x = x + y), ...`|
|Comparison	|`<, >, <=, >=, ==, !=, <=>, ><`|`0 < 1, 1 == 1, 1 <=> 'one, {1,2,3} >< {2,3,5}, ...`|
|Logical	|`&, |, !, and, or, not`|`true & false, me and you, eat|cook, not null, ...`|
|Identity	|`is , is not`	|`1 is true, 1 is not false, ...`|
|Membership	|`in, not in`	|`1 in [1,2,3], 'man' not in ['male', 'female'], ...`|
|Bitwise	|`&&, ||, ^^, <<, >>`|`1 && 1, 1 << 2, 0 ^^ 1, ...`|
|Others		|`+a, -a, a?, ~a`|`+1, -3.14, true?, ~1, ...`|

- Các kiểu dữ liệu:
	- [x] Chuỗi (string), kí tự (char) `"Hello Cup", 'Cup of Tea', 'a', "z", ...`
	- [x] Số nguyên (integer), số thực (decimal), số phức (complex) `123, 3.14, .6, 12+i, ...`
	- [ ] Logic (logic) `true, false, null, 0, 1`
	- [x] Thứ tự trong ASCII (ordinal) `65 <-> 'A', 97 <-> 'a', ...`
	- [x] Danh sách (list) `[1, '2', 3, "four", 5] ...`
	- [ ] Tập hợp (set) `{0, 1, 1, 2, 3, 5, 8, 13} ...`
	- [ ] Vỏ bọc (shell) `(true, false, true) ...`
	- [x] Từ điển (dict) `{"color":"red", "email":"bla@gmail.com"}`
	- [ ] Phạm vi (range) `[1;10] (0;5) (100; 1] [-oo; +oo)`

- [x] Biến và Hằng `date = '12/24/2021', exp = true, ...`
- [x] Chú thích `// this is comment`

- Câu điều kiện:
	- [x] Thường `if..elif..else`
	- [x] Lặp `when..is..else`

- Vòng lặp:
	- [x] for loop `for i in limit(1,10,1): ...`
	- [x] while loop `while..else`
	
- [x] Xử lí ngoại lệ `do..unless..last`
- [x] Hàm chức năng `let func(): ...`
- [ ] Lớp đối tượng `class Call: ...`
- [x] Chức năng sẵn có `say("doanh"), read("Today is: ") ...`
- [ ] liên kết module `use..of`
- [x] từ khóa `quit, continue, skip, return, throw, ...`
- Comming soon ...

### III. Ví dụ về tìm kiếm nhị phân trong Cup:

```
let BinarySearch(array, low, high, key): // same as find() built-in function
	while low <= high:
		mid = low + (high - low)\2
		if array[mid] == key:
			return mid
		elif array[mid] > key:
			high = mid - 1
		else:
			low = mid + 1
	return -1

// init array, key
array = [1,2,3,4,5,6,7,8,9] 
key = read("Enter your key: ")

// find key in array
output = BinarySearch(array, 0, 8, integer(key))

// result
say(key + " found at: " + string(output))
```

### IV. Bắt đầu thế nào?
Trên màn hình Command Prompt (cmd), nhập các lệnh sau:

```
git clone https://github.com/ArtistEatCode/PyCup.git
cd Cup
python -m Cup Test/hello_world.cup
```
