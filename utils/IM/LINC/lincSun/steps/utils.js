function get_losoto_config(step_name) {
    var par = ['soltab = ' + inputs.soltab]
    if (inputs.ncpu !== null && inputs.ncpu !== undefined) par.push('ncpu='+inputs.ncpu);
    par.push("[" + step_name + "]")
    par.push('operation=' + step_name)
    for(var field_name in inputs){
        if(field_name === 'input_h5parm' ||
           field_name === 'soltab' ||
           field_name === 'ncpu' || 
           field_name === 'execute') continue;

        if(inputs[field_name] === null ||
           inputs[field_name] === 'null') continue;
        
        if(inputs[field_name]["class"] !== undefined &&
           (inputs[field_name]["class"] ==="Directory" ||
            inputs[field_name]["class"] ==="File")){
            par.push(field_name+'='+inputs[field_name].path)
        } else {
            par.push(field_name+'='+inputs[field_name])
        }
    }
    return par
}

function concatenate_path(object_list){
    object_list.forEach(function (x, index, arr) {arr[index] = x.path;});
    return '[' + object_list.join(',') + ']'
    
}

function concatenate_path_wsclean(object_list){
    object_list.forEach(function (x, index, arr) {arr[index] = x.path;});
    return object_list.join(' ')
    
}