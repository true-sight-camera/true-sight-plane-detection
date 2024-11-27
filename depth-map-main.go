package main

import (
	"fmt"
	"log"
	"net/http"
)


func main() {
	router := http.NewServeMux()
	router.
	log.Fatal(http.ListenAndServe(":8080", router ))
}


func returnDepthMap(filename string) () {

}


func receiveFile(writer http.ResponesWriter, request * http.Request){
	request.ParseMultipartForm(32 << 20)
	var buf bytes.Buffer

	file, header, err := request.FormFile("file")
	if err != nil {
		panic(err)
	}
	defer file.Close()
	name := strings.Split(header.Filename, ".")
	fmt.Printf("File name %s\n", name[0])

	io.Copy(&buf, file)

	//do something with the contents here
	//here should parse the data
	
	contents := buf.String()
	fmt.Println(contents)

	buf.Reset()

	return
}