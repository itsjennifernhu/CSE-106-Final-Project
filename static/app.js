
likeObj_id = 0
function LikeOrDisLike(e,id,post_id,like_id)
{   
    if(likeObj_id == 0)
    {
        likeObj_id = parseInt(like_id)
    }

    var text = $(e).children("#"+id).html().trim()
    isLiked=false
    user_id = "{{current_user.id}}"

    if(text == 'Like')
    {
        $(e).children("#"+id).html('Liked')
        $(e).addClass("btn-Liked")
        isLiked = true
    }
    else 
    {
        $(e).children("#"+id).html('Like')
        $(e).removeClass("btn-Liked")
        isLiked = false

    }

    console.log(likeObj_id)
    $.ajax({
        type : 'post',
        data : {user_id : user_id ,  post_id: post_id , like : isLiked, like_id : likeObj_id},
        url : '/like-post',
        success : function(e)
        {
            likeObj_id=e['like_id']
            
        }
    })


}


    var loadFile = function(event) {
        var output = document.getElementById('imagePreview');
        output.src = URL.createObjectURL(event.target.files[0]);
        output.onload = function() {
          URL.revokeObjectURL(output.src) // free memory
        }
      };

      function share(btn,shared_to)
{
    post_id = "{{post_id}}"

    $.ajax({
            type : 'post',
            data : {post_id : post_id ,  shared_to: shared_to },
            url : '/share-post',
            success : function(e)
            {
                $(btn).text('shared')
                $(btn).addClass('btn-success')
                
            }
        })
}

isFollowing = false
function handFollowUser(e,id)
{

    var followed_id = id
    var is_following = false
    if($(e).html().trim() == 'Following')
    {
        is_following = false
    }
    else 
    {
        is_following = true
    }

    if(!is_following)
    {
        if(!confirm("Are you sure to unfollow this user?"))
        {
            return
        } 
    }
    
    $.ajax({
        'type' : 'post',
        'data' : {followed_id : id , is_following : is_following},
        'url' : '/follow-user',
        success : function(res)
        {

           if(is_following == false)
           {
               $(e).html('Follow')
                $(e).removeClass('btn-success')
           } 
           else 
           {
                $(e).html('Following')
                $(e).addClass('btn-success')
           }
        }
    })

}

