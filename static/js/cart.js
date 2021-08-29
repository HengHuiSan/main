var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var furnitureId = this.dataset.product
		var action = this.dataset.action
		console.log('furnitureId:', furnitureId, 'Action:', action)
		console.log('USER:', user)

		if (user == 'AnonymousUser'){
			addCookieItem(productId, action)
		}else{
			updateUserOrder(productId, action)
		}
	})
}