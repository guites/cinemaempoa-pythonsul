function getWalker(root) {
	const walker = document.createTreeWalker(
	    root, NodeFilter.SHOW_TEXT
	)
	const texts = [];
	let node;
	while ((node = walker.nextNode())) {
	  texts.push(node);
	}
	return texts;
}
